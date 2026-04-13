# How to Extend

RepoAudit is a customizable and multi-lingual code auditing framework. Currently, it supports the analysis of C, C++, Java, Python, and Go programs.
More bug detectors in these programming languages are under development.
If you want to customize RepoAudit for other bug types or programming languages, the following sections will help you.

## More Bug Types

If the bug type is an instance of a data-flow bug (i.e., detecting such bugs can be reduced to reachability analysis on a data-dependency graph),
you can follow the detection logic of inherent bug detectors built on [DFBScanAgent](https://github.com/PurCL/RepoAudit/tree/main/src/agent/dfbscan.py).
Here are the only two steps you need to take:

- Implement a sub-class of [DFBScanExtractor](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/dfbscan_extractor/dfbscan_extractor.py) for the programming languages you target and place it in the corresponding directories named [dfbscan_extractor](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/dfbscan_extractor/dfbscan_extractor.py). This extractor class offers the source/sink extractors for the detection. 

- Provide the prompt templates for intra-procedural data-flow analysis and path feasibility validation in the JSON files and place them in the corresponding sub-directories named [dfbscan](https://github.com/PurCL/RepoAudit/tree/main/src/prompt/Cpp/dfbscan/) in the directory [prompt](https://github.com/PurCL/RepoAudit/tree/main/src/prompt/).

You can refer to the implementations of existing sub-classes of [DFBScanExtractor](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/dfbscan_extractor/dfbscan_extractor.py) and the prompt templates. Notably, if the data-flow facts propagate in the same form as Null Pointer Dereference, Memory Leak, and Use-After-Free, you can reuse inherent prompt templates in [intra_dataflow_analyzer.json](https://github.com/PurCL/RepoAudit/tree/main/src/prompt/Cpp/dfbscan/intra_dataflow_analyzer.json) and [path_validator.json](https://github.com/PurCL/RepoAudit/tree/main/src/prompt/Cpp/dfbscan/path_validator.json).

Lastly, when you run RepoAudit for scanning, you need to inform the auditor of which categories of the bug types are, i.e., whether it is a source-must-reach-sink bug or source-must-not-reach-sink bug, by determining whether specifying the option `--is-reachable` in the run command.

## More Programming Languages

To support a new programming language, you need to follow the following steps:

- Add the repository link in the file [lib/build.py](https://github.com/PurCL/RepoAudit/tree/main/lib/build.py) and then execute `python lib/build.py` in the root directory for the installment.

- Follow existing parsing-based analyzers in the directory [src/tstool](https://github.com/PurCL/RepoAudit/tree/main/src/tstool), such as [Cpp_TSAnalyzer](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/analyzer/Cpp_TS_analyzer.py) and [Java_TSAnalzyer](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/analyzer/Cpp_TS_analyzer.py). Particularly, you need implement all the abstract methods in [TSAnalyzer](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/).

- Implement the corresponding bug detectors for the new programming languages. Please refer the instructions above step by step.

- Modify the entry of RepoAudit, i.e., [src/repoaudit.py](https://github.com/PurCL/RepoAudit/tree/main/src/repoaudit.py), and append more choices of languages and bug types to enable the analysis.
