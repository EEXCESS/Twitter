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

    query_filtered = """ SELECT DISTINCT ?label
        WHERE {{
            <http://zbw.eu/stw/thsys/%root> rdfs:label ?label
        } UNION {
            <http://zbw.eu/stw/thsys/%root> skos:narrower ?narrower .
            ?narrower rdfs:label ?label
        } UNION {
            <http://zbw.eu/stw/thsys/b> skos:narrower ?narrower .
            ?narrower skos:narrower ?narrower2 .
            ?narrower2 rdfs:label ?label
        } UNION {
            <http://zbw.eu/stw/thsys/%root> skos:narrower ?narrower .
            ?narrower skos:narrower ?narrower2 .
            ?narrower2 skos:narrower ?narrower3 .
            ?narrower3 skos:prefLabel ?label
        } UNION {
            <http://zbw.eu/stw/thsys/%root> skos:narrower ?narrower .
            ?narrower skos:narrower ?narrower2 .
            ?narrower2 skos:narrower ?narrower3 .
            ?narrower3 skos:narrower ?narrower4 .
            ?narrower4 skos:prefLabel ?label
        }
        FILTER langMatches( lang(?label), "%l" )
        }
        """

    # query_de = query.replace("%l", "de")
    query_filtered_b = query_filtered.replace("%l", "en")
    query_filtered_b = query_filtered_b.replace("%root", "b")

    query_filtered_v = query_filtered.replace("%l", "en")
    query_filtered_v = query_filtered_v.replace("%root", "v")

    g = Graph()
    # keyword download: http://zbw.eu/stw/versions/8.12/download/about.de.html
    g.parse("stw.nt", format="nt")
    result_b = g.query(query_filtered_b, initNs={"skos": SKOS, "zbwext": "http://zbw.eu/namespaces/zbw-extensions/"})
    result_v = g.query(query_filtered_v, initNs={"skos": SKOS, "zbwext": "http://zbw.eu/namespaces/zbw-extensions/"})

    keywords = []

    for row in result_b:
        keywords.append(row.label)

    for row in result_v:
        keywords.append(row.label)

    # keywords_sorted = sorted(keywords, key=str.lower)
    keywords_set = set(keywords)

    return keywords_set


extract_keywords()
