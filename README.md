### GreenGuy.me

This is a public copy of a full-stack Flask, SQLite3, and Bootstrap website I created as a useful portfolio project.

This website has a CV page which is generated using data stored in [JSON resume schema and hosted as a gist](https://gist.github.com/rsgn64/47c0a6ef15ba65847295a7626e6dbeed) which allows me to keep all my resume/CV information in a single data file.

The blogging portion is a custom design where I can write up blog posts in Jupyter Notebooks. This functionality exists in other platforms, but I wanted to create it myself. With this I can use [Quarto](https://quarto.org/) to convert my Jupyter Notebook files into really nice HTML files which have additional features like ToC, code block copy, citations, etc. and then add the output to a ZIP file and upload directly to this site to create a new blog post. The webapp modifies the Quarto output src locations to point to items on the server and organizes where html/image files are stored. Finally, the title and description is extracted and saved alongside the upload-date and post-name as metadata in a SQLite3 database.

I may need to build upon this as I add more blog posts such as adding a tagging system or comment/account system. Additionally, using Quarto on my PC to do the conversion isn't very robust as it could get updated and break what I've made. For now though, this is a good first webapp that's not only going to be useful, but I'm pretty proud to have self-taught myself. Thansk for reading :)
