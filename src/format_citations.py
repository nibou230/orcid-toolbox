from typing import Optional, Dict, Any, List
import re
import pandas as pd
import requests
from src.orcid_data import fetch_work_details

from pybtex.database import parse_string
import citeproc as cp
from citeproc import formatter
from citeproc.source.json import CiteProcJSON

# Helper function to strip curly braces from citation strings
def _strip_braces(text: str) -> str:
    return re.sub(r'[{}]', '', text)


# Helper function to safely extract BibTeX field values
def _get_field_value(field) -> Optional[str]:
    if field is None:
        return None
    if isinstance(field, str):
        return field
    if hasattr(field, 'value') and callable(field.value):
        try:
            return field.value()
        except Exception:
            return None
    return str(field) if field else None


# Helper function to convert BibTeX to CSL-JSON format for citeproc
def _bibtex_to_csl_json(bibtex: str) -> Optional[List[Dict[str, Any]]]:
    try:
        bib_data = parse_string(bibtex, "bibtex")
        csl_items = []
        
        for entry_key, entry in bib_data.entries.items():
            csl_item: Dict[str, Any] = {
                "id": entry_key,
                "type": _bibtex_type_to_csl_type(entry.type),
            }
            
            # Map common BibTeX fields to CSL-JSON
            title = _get_field_value(entry.fields.get("title"))
            if title:
                csl_item["title"] = title
                
            if "author" in entry.persons:
                authors = _parse_persons(entry.persons["author"])
                if authors:  # Only add if we got valid authors
                    csl_item["author"] = authors
                
            if "editor" in entry.persons:
                editors = _parse_persons(entry.persons["editor"])
                if editors:  # Only add if we got valid editors
                    csl_item["editor"] = editors
                
            year = _get_field_value(entry.fields.get("year"))
            if year:
                try:
                    year_val = int(year)
                    csl_item["issued"] = {"date-parts": [[year_val]]}
                except (ValueError, TypeError):
                    pass
                    
            journal = _get_field_value(entry.fields.get("journal"))
            if journal:
                csl_item["container-title"] = journal
                
            volume = _get_field_value(entry.fields.get("volume"))
            if volume:
                csl_item["volume"] = volume
                
            issue = _get_field_value(entry.fields.get("number") or entry.fields.get("issue"))
            if issue:
                csl_item["issue"] = issue
                
            pages = _get_field_value(entry.fields.get("pages"))
            if pages:
                csl_item["page"] = pages
                
            doi = _get_field_value(entry.fields.get("doi"))
            if doi:
                csl_item["DOI"] = doi
                
            url = _get_field_value(entry.fields.get("url"))
            if url:
                csl_item["URL"] = url
                
            publisher = _get_field_value(entry.fields.get("publisher"))
            if publisher:
                csl_item["publisher"] = publisher
            
            csl_items.append(csl_item)
        
        return csl_items if csl_items else None
    except Exception as e:
        print(f"Error converting BibTeX to CSL-JSON: {e}")
        import traceback
        traceback.print_exc()
        return None

# Helper function to map BibTeX entry types to CSL-JSON types
def _bibtex_type_to_csl_type(bibtex_type: str) -> str:
    type_map = {
        "article": "journal-article",
        "book": "book",
        "inproceedings": "paper-conference",
        "conference": "paper-conference",
        "proceedings": "book",
        "mastersthesis": "thesis",
        "phdthesis": "thesis",
        "techreport": "report",
        "inbook": "chapter",
        "incollection": "chapter",
        "misc": "entry",
        "unpublished": "entry",
    }
    return type_map.get(bibtex_type.lower(), "entry")

def _orcid_type_to_csl_type(orcid_type: str) -> str:
    type_map = {
        "journal-article": "journal-article",
        "book": "book",
        "conference-paper": "paper-conference",
        "proceedings": "book",
        "thesis": "thesis",
        "report": "report",
        "chapter": "chapter"
    }
    return type_map.get(orcid_type.lower(), "entry")

# Helper function to parse pybtex Person objects into CSL-JSON author/editor format
def _parse_persons(persons_list: List) -> List[Dict[str, str]]:
    result = []
    for person in persons_list:
        author_obj: Dict[str, str] = {}
        # pybtex Person object has first_names and last_names as attributes (lists) or methods
        try:
            first_names = person.first_names() if callable(person.first_names) else person.first_names
            if first_names:
                author_obj["given"] = " ".join(first_names)
        except (AttributeError, TypeError):
            pass
        
        try:
            last_names = person.last_names() if callable(person.last_names) else person.last_names
            if last_names:
                author_obj["family"] = " ".join(last_names)
        except (AttributeError, TypeError):
            pass
        
        if author_obj:
            result.append(author_obj)
    return result

# Fallback function to generate CSL item from ORCID work details when BibTeX is not available
def _generate_csl_item_from_orcid_work(work: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        # Build CSL item with careful None-value handling
        csl_item: Dict[str, Any] = {
            "id": str(work.get("put-code", "")),
            "type": _orcid_type_to_csl_type(work.get("type", "")),
        }
        
        # Only add title if it exists
        if work.get("title"):
            csl_item["title"] = work.get("title")
        
        # Only add author array if we have meaningful author data (not just from journal-title)
        # Skip author entirely rather than using journal-title as a fallback
        # as this produces invalid CSL-JSON
        
        # Only add issued if we have a year
        if work.get("publication-year"):
            try:
                year = int(work.get("publication-year"))
                csl_item["issued"] = {"date-parts": [[year]]}
            except (ValueError, TypeError):
                pass
        
        # Only add other fields if they're not None
        if work.get("journal-title"):
            csl_item["container-title"] = work.get("journal-title")
        if work.get("volume"):
            csl_item["volume"] = work.get("volume")
        if work.get("issue"):
            csl_item["issue"] = work.get("issue")
        if work.get("page"):
            csl_item["page"] = work.get("page")
        if work.get("doi"):
            csl_item["DOI"] = work.get("doi")
        if work.get("url"):
            csl_item["URL"] = work.get("url")
        
        # Only return if we have at least id and type
        if csl_item.get("id") and csl_item.get("type"):
            print(f"Generated fallback CSL item from ORCID work: {csl_item}")
            return csl_item
        return None
    except Exception as e:
        print(f"Error generating CSL item from ORCID work: {e}")
        import traceback
        traceback.print_exc()
        return None

# Convert CSL items to formatted citation string using citeproc
def _get_citation_from_csl_items(csl_items: List[Dict[str, Any]], csl_format: str, csl_locale: str) -> Optional[str]:
    try:
        # Use citeproc to format the citation
        bib_source = CiteProcJSON(csl_items)
        style = cp.CitationStylesStyle(csl_format, locale=csl_locale)
        bibliography = cp.CitationStylesBibliography(style, bib_source, formatter.plain)
        
        # Register the first item and get formatted bibliography
        first_item_id = csl_items[0]["id"]
        bibliography.register(cp.Citation([cp.CitationItem(first_item_id)]))
        # bibliography() returns list of formatted citations
        bib_list = bibliography.bibliography()
        if bib_list and len(bib_list) > 0:
            # Extract string from first item (could be string or tuple)
            citation_item = bib_list[0]
            if isinstance(citation_item, str):
                result = citation_item
            elif isinstance(citation_item, tuple) and len(citation_item) > 0:
                result = str(citation_item[0])
            else:
                result = str(citation_item) if citation_item else None
            return _strip_braces(result) if result else None
        return None
    except Exception as e:
        print(f"Error formatting CSL items with citeproc: {e}")
        import traceback
        traceback.print_exc()
        return None

# Get citations from the DOI Citation formatter when available
def _fetch_citation_from_doi(
    doi: str,
    csl_format: str,
    csl_locale: str,
    timeout: int = 10,
) -> Optional[str]:
    url = "https://citation.doi.org/format"
    # The API expects specific locale codes, so we map some common ones to the expected format.
    if csl_locale == "fr":
        csl_locale = "fr-CA"
    elif csl_locale == "en":
        csl_locale = "en-US"
    params = {
        "doi": doi,
        "style": csl_format,
        "lang": csl_locale,
    }
    headers = {
        "Accept": "text/plain",
        "User-Agent": "orcid-toolbox/1.0",
    }

    response = requests.get(url, params=params, headers=headers, timeout=timeout)
    # print(f"Requesting citation for DOI {doi} with format {csl_format} and locale {csl_locale}: HTTP {response.status_code}")
    response.raise_for_status()

    citation = response.text.strip()
    return citation or None

def _fetch_citation_from_orcid(orcid: str, put_code: str, csl_format: str, csl_locale: str, timeout: int = 10) -> Optional[str]:
    
    response = fetch_work_details(orcid, put_code, timeout=timeout)

    citation_retrieved = response.get("citation", {})

    if citation_retrieved:
        if citation_retrieved.get("citation-type") == "bibtex":
            bibtex = citation_retrieved.get("citation-value")
            # print(f"Received BibTeX for ORCID {orcid} put-code {put_code}: {bibtex}")
            
            # Convert BibTeX to CSL-JSON
            csl_items = _bibtex_to_csl_json(bibtex)
            if not csl_items:
                return None
            
            return _get_citation_from_csl_items(csl_items, csl_format, csl_locale)
            
        elif citation_retrieved.get("citation-type") == "formatted-unspecified":
            formatted_citation = citation_retrieved.get("citation-value")
            # print(f"Received formatted citation for ORCID {orcid} put-code {put_code}: {formatted_citation}")
            return _strip_braces(formatted_citation) if formatted_citation else None
        
    return None


def get_citations(works_df: pd.DataFrame, csl_format: str = "apa", csl_locale: str = "fr-CA") -> pd.DataFrame:

    output_df = pd.DataFrame(index=works_df.index)
    output_df["citation"] = None
    output_df["citation_error"] = None

    for idx, row in works_df.iterrows():
        doi = row.get("doi")
        if doi:
            try:
                citation = _fetch_citation_from_doi(doi, csl_format, csl_locale)
                output_df.at[idx, "citation"] = citation
            except requests.RequestException as exc:
                # print(f"Error extracting citation for DOI {doi}: {exc}")
                output_df.at[idx, "citation_error"] = str(exc)
        
        else:
            put_code = row.get("put-code")
            orcid = row.get("orcid")
            if put_code and orcid:
                try:
                    citation = _fetch_citation_from_orcid(orcid, put_code, csl_format, csl_locale)
                    output_df.at[idx, "citation"] = citation

                except Exception as exc:
                    # print(f"Error fetching citation for ORCID {orcid} put-code {put_code}: {exc}")
                    output_df.at[idx, "citation_error"] = str(exc)
            if citation is None:
                fallback_csl = _generate_csl_item_from_orcid_work(row)
                if fallback_csl:
                    try:
                        citation = _get_citation_from_csl_items([fallback_csl], csl_format, csl_locale)
                        output_df.at[idx, "citation"] = citation
                    except Exception as exc:
                        # print(f"Error generating citation from fallback CSL item for ORCID {orcid} and put-code {put_code}: {exc}")
                        output_df.at[idx, "citation_error"] = str(exc)
                
                else:
                    # print(f"No citation could be generated for ORCID {orcid} and put-code {put_code}!!")
                    output_df.at[idx, "citation_error"] = "No citation could be generated"

    return output_df

