<!--
SPDX-FileCopyrightText: 2024 - 2025 University of Manchester

SPDX-License-Identifier: apache-2.0
-->

# RSE-Repository-Template
This is a template repository to be used as the base for all new repos created for RSE projects. It comes with a set of default issues types and settings to ensure a standardised setup compliant with the department process.

# Immediate Set Up
The following steps will need to be performed immediately after creating the new repository to complete the set up.

## Branch Protection Ruleset
The first thing to do after creating your new repository from this template is to head to `Settings -> Rules -> Rulesets` then choose `Import Ruleset`. You will then need to import the `Key Branch Protection Rules.json` ruleset which is located in the RSE Team SharePoint under [`RSE Team -> Read-Only -> Tools`](https://livemanchesterac.sharepoint.com/sites/UOM-ITS-Research-IT/_layouts/15/download.aspx?UniqueId=b55bbc9bc39b4be29dafaa09b9359b48&e=B6kYNZ).

**This ruleset is designed to enforce a GitFlow development process as per the department policy. Please do not relax or disable these rules unless exceptional circumstances dictate it e.g. if an existing CI integration requires a rule to be relaxed.**

## Licensing and Copyright
Our team policy on software licensing and copyright can be found in the `RSE_Department_Ops_Policies.pdf` document, located in the RSE Team SharePoint under [`RSE Team -> Read-Only -> Policies and Processes`](https://livemanchesterac.sharepoint.com/:b:/r/sites/UOM-ITS-Research-IT/Shared%20Documents/RSE%20Team/Read-Only/Policies%20and%20Processes/RSE_Department_Ops_Policies.pdf). This policy is summarised below for convenience. If any discrepancies between the two arise then the policy document takes precedence over this readme file.

The default licence for an RSE project is the [Apache v2.0](http://www.apache.org/licenses/LICENSE-2.0) licence, a copy of which is provided in the file LICENSE. The customers licensing preference should have been gathered during the requirement gathering stage of the project; ask your project manager if this differs from the default.

Unless the project owners have made other agreements, the copyright of all works belongs to the University of Manchester. Check with your project manager to ensure that this is the case. Guidance on copyright issues are available from the [University of Manchester library](https://subjects.library.manchester.ac.uk/copyright/research).

To state the copyright, and use the Apache v2.0 licence, you should include the following text as a comment at the head of every source file you write:
```
   SPDX-FileCopyrightText: [yyyy] University of Manchester

   SPDX-License-Identifier: apache-2.0
```
Replace `[yyyy]` with the year that the code was first written.  The License Identifiers that are supported can be found in the [SPDX License Documentation](https://spdx.dev/learn/handling-license-info/).

In files which do not support the addition of comments (such as binary files), this can instead be included in an additional file adjacent to the original file with the same name followed by a .license extension, and containing just the lines above (e.g. a file called cat.jpg would have a licence file cat.jpg.license).  If the github action (see below) doesn't recognise a file format, it will generally add a .license file.  If you would prefer the license information to go into the file and you think it should be recognised, you can update the .extraformats file in the root of the repository with this information.  This file is formatted as a JSON dictionary, with the key being the filename or wildcard to match, and the value being one of the formats (see below for a list of formats supported).  For example, the following will recognise files with a cwl extension, and requirements.txt as python files, and so expect comments and put comments in using the python comment style:
```
{
"*.cwl": "python",
"requirements.txt": "python"
}
```
Note that this will look at the filename only, and won't work if you try to add a folder into the path. If you wish to add specific files (or wildcards) within folders, just put the filename.

If there are files that should not have a license on them and can therefore be ignored, the .licenseignore file in the root of the repository can be edited.  This follows the same standard as the .gitignore file format.

Note that there is a github action in this repository that will check that all files have the above annotations or .license file associated with them.  If this fails, an additional branch will be created which can be merged into the changes that you have committed.  A link will appear in the outputs of the GitHub actions task that will allow you to create a PR and merge this into your branch to allow the test to pass.  This link will also be added as a commit comment, which will be e-mailed to you if you have GitHub set up to send you notifications in this way. You should check the details of the suggested changes carefully to ensure it has done the right thing; any corrections can be made before merging, or can be done manually in the original branch if preferred.  

If the licence and/or copyright differs from the default, the action will have to be updated to reflect this.  Please edit the reuse-action in .github/workflows/license-copyright-add.yml to fix it, using the appropriate identifier from the [SPDX License List](https://spdx.org/licenses/).

### Format names supported
The following is a list of formats that you can put in the .extraformats file for recognition by the license annotation tool:
 - aspx
 - bat
 - bibtex
 - c
 - cpp
 - cppsingle
 - f
 - f90
 - ftl
 - handlebars
 - haskell
 - html
 - jinja
 - julia
 - lisp
 - m4
 - ml
 - plantuml
 - python
 - rst
 - semicolon
 - tex
 - man
 - vst
 - vim
 - xquery

## Setup `.gitignore`
Setup `.gitignore` according to your project needs, see `.gitignore` templates [here](https://github.com/github/gitignore/tree/main).


# Suggest Improvements
Please feel free to suggest improvements to this template by adding issues to [the repository](https://github.com/UoMResearchIT/RSE-Repository-Template/issues).
