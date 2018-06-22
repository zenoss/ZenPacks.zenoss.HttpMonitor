OUTPUT_HTML = /tmp/README.html

default: docs

docs:
	type top.css > README.html
	pandoc header.md --template=template.html >> README.html
	pandoc releases.md --template=template.html >> README.html
	pandoc body.md -f markdown_mmd --template=template.html --table-of-contents >> README.html

