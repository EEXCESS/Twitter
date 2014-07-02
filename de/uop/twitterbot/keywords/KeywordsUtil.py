from rdflib import Graph
from rdflib.namespace import SKOS


def extract_keywords():
    # a zbwext:Descriptor
    # skos:altLabel

    query = """SELECT DISTINCT ?label
        WHERE {{
                ?s a zbwext:Descriptor .
                ?s skos:prefLabel ?label
                FILTER langMatches( lang(?label), "%l" )
            }
            UNION {
                ?s a zbwext:Descriptor .
                ?s skos:altLabel ?label
                FILTER langMatches( lang(?label), "%l" )
            }
            UNION {
                ?s a zbwext:Thsys .
                ?s rdfs:label ?label
                FILTER langMatches( lang(?label), "%l" )
            }
        }"""

    # query_de = query.replace("%l", "de")
    query_en = query.replace("%l", "en")

    g = Graph()
    # keyword download: http://zbw.eu/stw/versions/8.12/download/about.de.html
    g.parse("../stw.nt", format="nt")
    result = g.query(query_en, initNs={"skos": SKOS, "zbwext": "http://zbw.eu/namespaces/zbw-extensions/"})

    keywords = []

    for row in result:
        keywords.append(row.label)

    # keywords_sorted = sorted(keywords, key=str.lower)
    keywords_set = set(keywords)

    return keywords_set


extract_keywords()
