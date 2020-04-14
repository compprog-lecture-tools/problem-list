# Problem list

Generate webpages that list problems from a problem repo in an easily accessable manner.
Problems are shown and filterable by their difficulty, tags, and other aspects.
Links are provided to a problems directory in the repository, as well as pdfs of its statement and notes.
The pdfs are generated alongside the webpages.

The generated output consists of static html and pdf files.
The `deploy` directory contains helper scripts to set up a password protected hosting for these, as well as easy updating of them from a CI job.

For running CI jobs, a container is provided in `docker` that contains all necessary tools preinstalled.
Additionally, the two `ci-cache-*` scripts allow caching the build directories of problems, to avoid rebuilding unchanged problems when generating their pdfs.
