# Automated Diagnostic Log Injector (ADLI)

This tool is used to inject diagnostic logs into a python program. For more information on diagnostic logs, please see the [background](#Background) section. 
The CDL logs generated by running the injected source code can be viewed in the [Diagnostic Log Viewer][dlv]. 

## Program Log Injection

To inject logs into a single python program follow usage instructions.

### Usage
Run the tool using the following command (using Python 3.9+):

  ```shell
  python adli.py <source_file>
  ```
In the output folder, this tool will create a folder with the same name as the source program. This folder will contain the injected source code for the program. 

Running the program will generate a CDL file that can be viewed in the diagnostic log viewer.

### Optional Metadata File

The optional metadata information for the program can be included in the program using comments. An example is provided below and can be found in adli.py in this repo. The metadata will be included in the header of the CDL file. If no metadata is provided, the metadata key in the header of the CDL file will be an empty object.

An example of the adli metadata comment:
```
'''
{
    "type": "adli_metadata",
    "name": "ADLI",
    "description": "A tool to inject diagnostic logs into a python program.",
    "version": "0.0",
    "language": "python"
}
'''
```

### Arguments

#### Optional
- `-sysinfo` : A path to the System Definition File (SDF). 
  - This information is used when injecting logs into all programs in a system. 
  - If no path is provided, then the sysinfo key in the header of the CDL file will be an empty object.

- `-uid` : A unique id representing this execution of the ADLI tool. 
  - When injecting system logs using `adli_system.py`, this uid is passed to all programs in the system.
  - If no uid is provided, a new one is generated.

## System Log Injection

`adli_system.py` is a helper program which can be used to inject logs into multiple programs in the system. A System Definition File (SDF) is used to define the system by providing a name, id, version and description. It also includes absolute paths to a list of programs which should be injected with logs. After running the program, in the output folder, each log injected program can be found in a folder with the same name as each program.

Note: This feature will be updated to change the way that systems are defined. It would be more convenient to define the programs in the system using their repos and commit ID's. This tool will then have to clone the repos, inject the logs and save them to the output folder. When this process is integrated with a deployment workflow, the injected source will also be deployed.

### Usage
Run the tool using the following command (using Python 3.9+):
  ```shell
  python adli_system.py <path_to_SDF_file>
  ```

An example of the System Definition File is provided below:
```
{
    "metadata": {
        "name": "Distributed Sorting System",
        "description": "This system accepts sorting jobs form clients over a webksocket and assigns them to distributed works. It returns the sorted list.",
        "systemVersion": "0.0",
        "systemId" : "1234"
    },
    "programs": [
        "/home/dev/repo/sample-system/simulatedClient/simulatedClient.py",
        "/home/dev/repo/sample-system/workers/radixSort/radixSortWorker.py",
        "/home/dev/repo/sample-system/workers/mergeSort/mergeSortWorker.py",
        "/home/dev/repo/sample-system/workers/bubbleSort/bubbleSortWorker.py",
        "/home/dev/repo/sample-system/jobHandler/jobHandler.py"
    ]
}
```

The system definition file and a unique id associated with this deployment of the system are passed into the ADLI tool using command line arguments. This information is included in the header of the CDL file and is used by ASP to automatically assemble the system and process it.

Using this information, we will be able to uniquely identify every system and its unique deployment to automatically process them.

# How does it work? 

Note: Parts of this section are outdated and some features are not explored. It will be updated in a coming update.

The ADLI tool is designed to inject diagnostic logs into a python program. It uses the official python abstract syntax
tree library to parse the code and inject the logs.

ProgramProcessor:
* Accepts a source path to a python program.
* Finds all locally imported source files in the program.
* Parses each source file into an AST and processes it with the LogInjector class.

LogInjector:
* Uses the NodeTransformer class to visit nodes in the tree and inject diagnostic logs.
* Maintains a log type and variable map for each id and also track which function each log type and variable are part of. 

CollectVariableNames:
* Used to collect variable names from a given node by visiting child nodes.
* Generates a unique varid for each variable.
* Saves the varid and variable metadata (name, column etc..).
* For assign statements, it extracts the specific key that is being updated.

The logging setup is added to the injected AST's and they are unparsed and placed in the output folder while preserving the original program's folder structure. At this point, the injected source code can be run and it will generate a log file which can be viewed using the [Diagnostic Log Viewer][dlv].

# Background

> [!NOTE]  
> A more detailed introduction to diagnostic logging and the diagnostic tools it enables is in development.

CDL files are generated through a process called Diagnostic Logging (DL) in which the log type, variable values and exceptions for each statement in the program are logged. Diagnostic logging is enabled by Automated Diagnostic Log Injector (ADLI) tools, which automatically insert the necessary log statements to extract the diagnostic information.

The ADLI tool uses Abstract Syntax Trees (AST's) to traverse through the structure of the program to extract variable names and insert the necessary log statements for logtypes and variables. It inserts try except statements to catch any exceptions which occured when running the program and logs it. It also inserts a log statement to inject the log type map of the program into the header of the CDL file. This maps every logtype and variable to a line in the program. The enables us to only log the logtype id, effectively compressing the logtypes by default.

When diagnostic logs are ingested by CLP, having a map of the variables and log types will result in improved performance and a simpler implementation. It will be possible to further compress the logs by applying data specific compression to variables based on their variable type.

Using Diagnostic Logging, it is possible to build a fully automated log based diagnostic solution that can perform automated root cause analysis. In the next level of abstraction, it also automates the analysis, maintenance and recovery of systems. While all types of systems will benefit from diagnostic logging, distributed systems will benefit the most.

A simplified diagram of the diagnostic solution enabled by diagnostic logging is provided below.

![image](https://github.com/user-attachments/assets/429c667b-3b51-4171-becf-9bf946d0579f)

# Providing feedback

You can use GitHub issues to [report a bug][bug-report] or [request a feature][feature-req].

[bug-report]: https://github.com/vishalpalaniappan/asp-adli-python/issues/new?template=bug_report.md
[feature-req]: https://github.com/vishalpalaniappan/asp-adli-python/issues/new?template=feature_request.md
[dlv]: https://github.com/vishalpalaniappan/diagnostic-log-viewer
