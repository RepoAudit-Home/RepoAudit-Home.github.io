# Project Architecture 
## Overview

RepoAudit is a multi-agent framework. Each [agent](https://github.com/PurCL/RepoAudit/tree/main/src/agent/) targets a specific code auditing task, such as data-flow bug detection, program slicing, and general bug detection. An agent can utilize parsing-based analyzers (e.g., the interfaces of [src/tstool/analyzer/TS_analyzer.py](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/analyzer/TS_analyzer.py)), LLM-driven analyzers (e.g., different LLM-based tools in [src/llmtool](https://github.com/PurCL/RepoAudit/tree/main/src/llmtool/)), and even [agents](https://github.com/PurCL/RepoAudit/tree/main/src/agent/).

When scanning a repository, we first initialize a parsing-based analyzer (i.e., an instance of [TSAnalyzer](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/analyzer/TS_analyzer.py)) for code indexing and then invoke a specific agent for scanning. The results of the parsing-based analyzer, agent, and final results (such as bug reports) are maintained in the memory of RepoAudit.

Here is a pipeline of RepoAudit

```

                         +-------------+     +---------+      
                         |    TSTool   |     | LLMTool |
                         +-------------+     +---------+
                            ↑        ↓            ↓
            +----------------+     +-------------------+     +------------------+
Code   →    |   TSAnalyzer   |  →  |      Agents       |  →  |      Reports     |
            | (AST Parsing)  |     |(Semantic Analysis)|     |  (Final Results) |
            +----------------+     +-------------------+     +------------------+
                    ↓                     ↑    ↓                       ↓
        +--------------------------------------------------------------------------+  
        |   [Syntactic Memory]       [Semantic Memory]         [Report Memory]     |
Memory  |     Syntactic Info        Semantic Properties          Scan Report       |
        |  (Value/Function/API)        (Agent State)          (Bug/Debug results)  |
        +--------------------------------------------------------------------------+
```

## Core Components

### TSAnalyzer: Parsing-based Analysis

RepoAudit leverages [tree-sitter](https://tree-sitter.github.io/tree-sitter/) to derive the abstract syntax tree (AST) of the repository code.
Specifically, it extracts the basic constructs of each function, including critical values (e.g., parameters, arguments, output values, and return values), branches (e.g., if-statements), and loops (e.g., for-loops and while-loops). 
Based on the derived constructs, it further constructs a call graph (based on function names and parameter/argument numbers), control-flow order analysis, and CFL-reachability analysis.
Notably, such parsing-based analysis may approximate the semantic properties, especially caller-callee relationships, though it may not be sound or complete in cases involving class hierarchy and function pointers.

The above functionalities are supported by different sub-classes of [TSAnalyzer](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/analyzer/TS_analyzer.py), targeting different programming languages.
The source code is located in the directory [src/tstool/analyzer](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/analyzer/).

### Agent

An agent is a component targeting a specific code auditing task, such as program slicing, debugging, bug detection, program repair. Currently, RepoAudit only targets the bug detection task, while it can be easily extended to support other tasks. Notably, as a multi-agent framework, an agent in RepoAudit can leverage the results of other agents. In the file [src/agent/agent.py](https://github.com/PurCL/RepoAudit/tree/main/src/agent/agent.py), we offer the definition of the base class [Agent](https://github.com/PurCL/RepoAudit/tree/main/src/agent/agent.py), which have the following several sub-classes focusing on concrete tasks:

#### MetaScanAgent

[MetaScanAgent](https://github.com/PurCL/RepoAudit/tree/main/src/agent/metascan.py) is a simple agent for demo. It wraps the parsing-based analyzer without additional symbolic or neural analysis.

#### DFBScanAgent

[DFBScanAgent](https://github.com/PurCL/RepoAudit/tree/main/src/agent/dfbscan.py) is our current open-sourced agent for data-flow bug detection. It implements the analysis workflow presented in this [paper](https://arxiv.org/abs/2501.18160). Our implemented version can support the detection of the following bug types in different programming languages.

| Bug Type                    | C   | C++ | Java | Python | Go  |
|-----------------------------|-----|-----|------|--------|-----|
| Null Pointer Dereference    | ✓   | ✓   | ✓    | ✓      | ✓   |
| Memory Leak                 | ✓   | ✓   |      |        |     |
| Use After Free              | ✓   | ✓   |      |        |     |

### TSTool: Parsing-based Tools

To support a specific agent, we currently offer several additional parsing-based tools for different bug types in different programming languages. For example, in the detection of Null Pointer Dereference (NPD) in C++ programs, we need to identify the source values (i.e., potential NULL values).
Utilizing the interfaces offered by [TSAnalyzer](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/analyzer/TS_analyzer.py), we create [Cpp_NPD_Extractor](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/dfbscan_extractor/Cpp/Cpp_NPD_Extractor.py) for the extraction of NULL values.

You can also follow the definition of [Cpp_NPD_Extractor](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/dfbscan_extractor/Cpp/Cpp_NPD_Extractor.py) when you define your own agent and the relevant parsing-based tools.
We will also integrate a synthesis agent into RepoAudit to synthesize specific parsing-based tools, such as source extractors, by following the design in our previous work [LLMDFA](https://neurips.cc/virtual/2024/poster/95227).

### LLMTool: LLM-driven Tools

LLM-driven tools enable semantic analysis of source code without compilation.
Similar to traditional IR-based program analyzers,
these tools derive program facts or transform source code for further analysis, functioning similarly to LLVM passes in LLVM-based C/C++ analyzers.

As shown in the file [src/llmtool/LLM_tool.py](https://github.com/PurCL/RepoAudit/tree/main/src/llmtool/LLM_tool.py) containing the base class [LLMTool](https://github.com/PurCL/RepoAudit/tree/main/src/llmtool/LLM_tool.py),
an instance of a LLM-driven tool recieves and returns a specific form of input and output objects, respectively.
When defining a LLM-driven tool, i.e., the sub-class of [LLMTool](https://github.com/PurCL/RepoAudit/tree/main/src/llmtool/LLM_tool.py), we also need to define the sub-classes of `LLMToolInput` and `LLMToolOutput`.
Also, we have to provide the corresponding prompting template in the directory [src/prompt](https://github.com/PurCL/RepoAudit/tree/main/src/prompt/).

Consider the LLM-driven tools used by [DFBScanAgent](https://github.com/PurCL/RepoAudit/tree/main/src/agent/dfbscan.py).
We include two LLM-driven tools in the directory [src/llmtool/dfbscan](https://github.com/PurCL/RepoAudit/tree/main/src/llmtool/dfbscan/).

- [IntraDataFlowAnalyzer](https://github.com/PurCL/RepoAudit/tree/main/src/llmtool/dfbscan/intra_dataflow_analyzer.py) derives the data-flow facts along different program paths in single functions. It corresponds to `explorer` in the [paper](https://arxiv.org/abs/2501.18160).

- [PathValidator](https://github.com/PurCL/RepoAudit/tree/main/src/llmtool/dfbscan/path_validator.py) validates the feasiblity of a program path. It corresponds to `validator` in the [paper](https://arxiv.org/abs/2501.18160).


### Memory

As a multi-agent framework for code auditing, RepoAudit contains three kinds of memory, which are implemented in the directory [src/memory](https://github.com/PurCL/RepoAudit/tree/main/src/memory/).

#### Syntactic Memory

Syntactic memory maintains critical constructs for code auditing. RepoAudit mainly focuses on the program values in different functions.
Utilizing [TSAnalyzer](https://github.com/PurCL/RepoAudit/tree/main/src/tstool/analyzer/TS_analyzer.py), it stores the [Function](https://github.com/PurCL/RepoAudit/tree/main/src/memory/syntactic/function.py), [API](https://github.com/PurCL/RepoAudit/tree/main/src/memory/syntactic/api.py), and [Value](https://github.com/PurCL/RepoAudit/tree/main/src/memory/syntactic/value.py) info in the syntactic memory.
These three constructs are then retrieved by agents when the agents invoke the LLM-driven tools.

In the future, we may need to extend the syntactic memory and maintain more expressive compilation-independent IR constructs.

#### Semantic Memory

Semantic memory maintains the intermediate states of agents. 
For each agent, we define a corresponding state as the sub-class of [State](https://github.com/PurCL/RepoAudit/tree/main/src/memory/semantic/state.py).
For example, [DFBScanState](https://github.com/PurCL/RepoAudit/tree/main/src/memory/semantic/dfbscan_state.py) stores the data-flow facts along different paths and also the relevant parameters/return values/arguments/output values.
Based on the semantic memory, the agents can finally compute the outputs and obtain the reports of the agents.

#### Report Memory

Reports maintain the final results of the agents.
Currently, there is only one type of reports, i.e., bug reports and debug reports, 
which are the outputs of the end-user agents including [DFBScanAgent](https://github.com/PurCL/RepoAudit/tree/main/src/agent/dfbscan.py).
For [MetaScanAgent](https://github.com/PurCL/RepoAudit/tree/main/src/agent/metascan.py), since they do not compute additional program facts,
we do not explicitly define its specific report format.

## Project Structure

For your reference, we append the project structure as follows:

```
# In src directory
├── agent                # Directory containing different agents for different uses
│   ├── agent.py         # The base class of agent
│   ├── dfbscan.py       # The agent for data-flow bug detection. Implemented in RepoAudit
│   └── metascan.py      # The agent for syntactic analysis
├── llmtool              # Directory for LLM-based analyzers
│   ├── LLM_tool.py      # The base class of LLM-based analyzers as tools
│   ├── LLM_utils.py     # Utility class that invokes different LLMs
│   └── dfbscan          # LLM tools used in dfbscan
│       ├── intra_dataflow_analyzer.py  # LLM tool: Collect intra-procedural data-flow facts
│       └── path_validator.py   # LLM tool: Validate the path reachability
├── memory
│   ├── report           # Reports of agents 
│   │   └── bug_report.py
│   ├── semantic         # Semantic properties focused in different agents
│   │   ├── dfb_state.py
│   │   ├── metascan_state.py
│   │   └── state.py
│   └── syntactic        # Syntactic properties, i.e., AST info
│       ├── api.py
│       ├── function.py
│       └── value.py
├── tstool
│   ├── analyzer         # parsing-based analyzer
│   │   ├── Cpp_TS_analyzer.py      # C/C++ analyzer
│   │   ├── Go_TS_analyzer.py       # Go analyzer
│   │   ├── Java_TS_analyzer.py     # Java analyzer
│   │   ├── Python_TS_analyzer.py   # Python analyzer
│   │   ├── TS_analyzer.py          # Base class
│   └── dfbscan_extractor # Extractors used in dfbscan (based on parsing)
│       ├── Cpp
│       │   ├── Cpp_MLK_extractor.py
│       │   ├── Cpp_NPD_extractor.py
│       │   ├── Cpp_UAF_extractor.py
│       ├── Java
│       │   └── Java_NPD_extractor.py
│       └── dfbscan_extractor.py
├── prompt # Prompt templates
│   ├── Cpp
│   │   └── dfbscan    # Prompts used in dfbscan for Cpp program analysis
│   │       ├── intra_dataflow_analyzer.json
│   │       └── path_validator.json
│   ├── Go
│       └── dfbscan    # Prompts used in dfbscan for Python program analysis
│   ├── Java
│   │   └── dfbscan    # Prompts used in dfbscan for Java program analysis
│   │       ├── intra_dataflow_analyzer.json
│   │       └── path_validator.json
│   └── Python
│       └── dfbscan    # Prompts used in dfbscan for Python program analysis
└── ui                   # UI classes
│   ├── logger.py        # Logger class
│   └── web_ui.py        # Web UI class
├── repoaudit.py         # Main entry of RepoAudit
├── run_repoaudit.sh     # Script for analyzing one project
```