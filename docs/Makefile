OUTPUT_HTML = /tmp/README.html

default: docs

docs:
	cat top.css > $(OUTPUT_HTML)
	pandoc header.md --template=template.html >> $(OUTPUT_HTML)
	pandoc releases.md --template=template.html >> $(OUTPUT_HTML)
	pandoc body.md -f markdown_mmd --template=template.html --table-of-contents >> $(OUTPUT_HTML)

production: docs
	python docs.py