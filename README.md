# Automated Diagnostic Log Injector (ADLI)

This program allows you to inject diagnostic logs into a python program. For more information on
diagnostic logs, please see the background section.

# Usage

Run the tool using the following command (using Python 3.9+):

  ```shell
  python adli.py <source_path>
  ```

The program will generate an output folder which contains a folder with the programs name.
In this folder, you will find the injected source fils with the original folder structure.

Running the program will generate a CDL file that can be viewed in the diagnostic log viewer.

> [!NOTE]  
> Currently the tool injects logtype and exception log statements. Support for variable log statements
> will be added to the public repo soon.

# How does it work? 

The ADLI tool is designed to inject diagnostic logs into a python program. It uses the official python abstract syntax
tree library to parse the code and inject the logs.

ProgramProcessor:
* Accepts a source path to a python program.
* Initializes a file queue with the source path and processes the queue. 
* Each file in the queue is processed with the LogInjector class.
* Any local imports found and added to the queue and processed.

LogInjector:
* Parses the python source code into an AST.
* Creates an empty AST to populate with the injeted nodes.
* Creates a simplified syntax tree(SST) to map the logtype/variables to a position in the program.
* Recursively processes the AST until all nodes are consumed with injected variable, logtype and exception log statements.

NodeExtractor:
* The NodeExtractor class is used to extract metadata from AST nodes (variables etc.) and to generate the logging statements.

SST:
* The SST class is used to add nodes to the simplified syntax tree tree and assign logtype ID's.

The logging setup is added to each of the injected AST's and they are unparsed into injected source code and placed in the output folder while preserving the original folder structure.

# Background

> [!NOTE]  
> A more detailed introduction to diagnostic logging and the diagnostic tools it enables is in development.

CDL files are generated through a process called Diagnostic Logging (DL) in which the log type, variable values and exceptions for each statement in the program are logged. Diagnostic logging is enabled by Automated Diagnostic Log Injector (ADLI) tools (coming soon!), which automatically insert the necessary log statements to extract the diagnostic information.

The ADLI tool uses Abstract Syntax Trees (AST's) to traverse through the structure of the program to extract variable names and insert the necessary log statements. It surrounds each statement in the program with a try structure to catch and log exceptions. It also inserts a log statement to inject the Simplified Syntax Tree (SST) of the program into the header of the CDL file. The SST maps every logtype and variable to a line in the program. The enables us to only log the logtype id, effectively compressing the logtypes by default.

When diagnostic logs are ingested by CLP, having a map of the variables and log types will result in improved performance and simpler implementation. It will be possible to further compress the logs by grouping variable values by name.

Using Diagnostic Logging, it will be possible to build an automated log based diagnostic solution that can perform automated root cause analysis. A simplified diagram of the diagnostic solution enabled by diagnostic logging is provided below.

![Simplified ASP System Diagram](docs/Simplified_System_Diagram_ASP.png)

# Providing feedback

You can use GitHub issues to [report a bug][bug-report] or [request a feature][feature-req].

[bug-report]: https://github.com/vishalpalaniappan/asp-adli-python/issues/new?template=bug_report.md
[feature-req]: https://github.com/vishalpalaniappan/asp-adli-python/issues/new?template=feature_request.md

# Docs

In development.

# Contributing

In development.
