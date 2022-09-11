# The Backend library

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and "OPTIONAL"
in this document and all other files in this directory, including but not limited to python docstrings,
are to be interpreted as described in RFC 2119.

## How to use
1. Set `Scheduler.default_scheduler` to the `DebugScheduler` for the start, you might want to use the `UserRoundRobinScheduler`
2. Run `AlgorithmLoader.set_algorithm_root_dir` and define the directory in which your algorithms will be located.
The elements directly in this directory should not conflict with the other modules in your pythonpath,
as this directory will be added to your pythonpath (done automatically by the `AlgorithmLoader`). 
3. You are ready to go.
Create a `DatasetCleaning` or `Execution` and run `.schedule()` on it.
The library will take care of the rest.
## How it works
After doing some prep work `Task.schedule()` will submit the `Task` to the `Scheduler` used (singleton).
If the Scheduler decides it is time to start, the `Schedulable` has the opportunity to do some further prep on the main process (`run_before_on_main`), after which `do_work` will be called, where most of the work happens. After that finishes `run_later_on_main` will be called.

### Cleaning
The cleaning simpy runs in th do_work method, reads the dataset, runs the CleaningSteps one after another and then saves the result.
Close to trivial.

### Execution 
Algorithm executions are a lot more complex. 1st the dataset is loaded into shared memory and the subspaces generated, then `ExecutionSubspace`s are created for each subspace. Each creates an array in shared memory with the subspace array from the main dataset shared memory. After that an `ExecutionElement` is created for each Algorithm, which then runs that algorithm on that subspace array. `ExecutionElement`s are run before new `ExecutionSubspace`s are started, which are prioritized over new `Execution`s again.

All in all that means that even if your outlier detection is only running single threaded this Library will help you make perfect use of your CPU cores and RAM.

### Outlier detection algorithms
Outlier detection algorithms to be used must be contained in the `AlgorithmLoader`'s root_dir. They must be a single python (.py) file.
That file must contain a class which has the same name as the python file (case-insensitive). That classmust be a subclass of the `pyod.models.base.BaseDetector` class and implements the required methods
(see [pyod BaseDetector documentation](https://pyod.readthedocs.io/en/latest/api_cc.html#pyod.models.base.BaseDetector)). That class must not be abstract or contain any abstract method. The algorithm file may contain further contents including but not limied to further classes. The algorithm file may come with dependencies packed into the same file. The algorithm file may use pyods dependencies. The algorithm file should not depend on packages in the `backend_library/src/pyproject.toml` that are not pyod dependencies.


### Further features
 Any task can aborted with a capable `Scheduler` (like the `UserRoundRobinScheduler`) without leaking memory or anything.

## Structure

### Root (backend)

On the root level of the sources there are basic classes and Interfaces, no heavy-lifting is done here.

### backend.Scheduler

Contains the code for the scheduling and the interfaces for Schedulers and Schedulables. Th DebugScheduler does not do any Scheduling and just executes everything directly. The UserRoundRobinScheduler uses Multiprocessing and some basic scheduling w/o timeslices.

### backend.metric

Contains code for calculating different metrics on execution results.

### backend.task

Contains helpers for the different Tasks

### backend.task.cleaning

Contains all the code for dataset cleaning including the cleaning steps themselves.

### backend.task.execution

Contains the code for dynamically loading outlier detection algorithms and some other helpers for execution

### backend.task.execution.subspace

Contains the code for generating subsapces and related stuff.

### backend.task.execution.core

This is the place where the magic happens. Contains the code for actually running algorithms on the datasets efficiently.  

## Tests

A big amount of tests is contained in the test-Directory, reaching a coverage of 99,x%
