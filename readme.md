indexer.py -> primary file which will take wikipedia dump as input and will generate primary indexes
merge.py -> File that will merge primary indexes and will create secondary indexes
heap.py -> custom heap implementation of merge, heap element is combination of token , file pointer, and posting list
filehandling.py -> logic to merge and create secondary index
search.py -> Will take queries as input and will generate file containing searched output titles.