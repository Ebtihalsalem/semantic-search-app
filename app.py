from flask import Flask, request, render_template
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

sparql = SPARQLWrapper("http://localhost:3030/ontology/sparql")
PREFIX = """
PREFIX gpo: <http://www.semanticweb.org/pc/ontologies/2025/3/Graduati_on_Projects_Ontology#>
"""

@app.route('/', methods=['GET', 'POST'])
def search():
    query_input = None
    projects = []

    if request.method == 'POST':
        query_input = request.form.get('q')

        query = PREFIX + f"""
        SELECT ?title ?summary ?year ?student ?supervisor ?dept ?link WHERE {{
          ?project a gpo:Project ;
                   gpo:projectName ?title ;
                   gpo:abstract ?summary ;
                   gpo:enrolledInDepartment ?dept ;
                   gpo:isSupervisedBySupervisor ?supervisor ;
                   gpo:isFinalFileOf ?file .
          ?file gpo:downloadLink ?link .
          OPTIONAL {{ ?project gpo:year ?year . }}
          OPTIONAL {{ ?student gpo:worksOnProject ?project . }}
          FILTER(CONTAINS(LCASE(?title), LCASE("{query_input}")))
        }}
        """
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        temp = {}
        for r in results["results"]["bindings"]:
            title = r.get("title", {}).get("value", "")
            if title not in temp:
                temp[title] = {
                    "title": title,
                    "summary": r.get("summary", {}).get("value", ""),
                    "year": r.get("year", {}).get("value", ""),
                    "supervisor": r.get("supervisor", {}).get("value", "").split("#")[-1],
                    "dept": r.get("dept", {}).get("value", "").split("#")[-1],
                    "link": r.get("link", {}).get("value", ""),
                    "students": []
                }
            student = r.get("student", {}).get("value", "")
            if student:
                temp[title]["students"].append(student.split("#")[-1])

        projects = list(temp.values())

    return render_template('index.html', query=query_input, projects=projects)

if __name__ == '__main__':
    app.run(debug=True)