# 🕵️‍♀️
The project implements a simple search to find tickets and users by field. The search builds an inverted index structure which is explained in depth below.

### Assumptions
- I have inferred the user and ticket schemas from the example files, this solution requires a hardcoded schema definition. Initially when I wrote this I included a method to generate the schema for a set of records by finding the superset of columns present in all fields. I decided for simplicity's sake to omit this.
- The relationship between user and ticket is defined by `user._id` == `ticket.assignee_id`

### How do I run it?

Only dependency is `Docker`

Navigate the root of the directory build and tag the docker container

- `docker-compose up`
- `docker-compose run tests`
- `docker-compose run search`

### How does the search work?

In my implementation of an inverted index I have used a nested dictionaries. The dictionary keys each document by every field and value in that document.

Consider the following document with `id = 1`
```python
{
  "name": "saskia",
  "age": 1,
  "noises": [
    "meow",
    "purr",
    "sniff",
    "schnuffle"
  ],
  "temperament": "agreeable",
  "coat": "short"
}
````
I'm going to insert it into an empty inverted index `{}`
```python
{
  "name": {
    "saskia": [1]
  },
  "age": {
    "1": [1]
  },
  "noises": {
    "meow": [1],
    "purr": [1],
    "sniff": [1],
    "schnuffle": [1]
  },
  "temperament": {
    "agreeable": [1]
   },
  "coat": {
    "short": [1]
  }
}
```

Let's add another document with `id = 2`
```python
{
  "name": "bo",
  "age": 1,
  "noises": [
    "rawr",
    "purr",
    "yawn",
    "meow"
  ],
  "temperament": "skittish",
  "coat": "long"
}
````


Now the index looks like
```python
{
  "name": {
    "saskia": [1],
    "bo": [2]
  },
  "age": {
    "1": [1, 2]
  },
  "noises": {
    "meow": [1, 2],
    "rawr": [2],
    "purr": [1, 2],
    "sniff": [1],
    "schnuffle": [1],
    "yawn": [2]
  },
  "temperament": {
    "agreeable": [1],
    "skittish": [2]
   },
  "coat": {
    "short": [1],
    "long": [2]
  }
}
```

If we want to find all the cats who purr we simple return `index[noises][purr]` and we get documents `[1, 2]`. If we want to find all cats named saskia we return `index[name][saskia]` and we get document `[1]`.

### Why an inverted index?

The inverted index strikes a good balance of ease of implementation and performance. It is especially suited to our usecase of full word searching as keys can be retrieved instantly given the entire word. My dictionary based implementation takes `O(n)` to build where `n = the total number of attributes in each document of our input data` and `O(1)` to query.

Some other options I considered
- Don't index input data just linearly search on every query
    - In a distributed environment, where the data is sharded across machines this could be a viable option especially if there is a high ratio of writes to reads.
    - In our use case, since the data can fit on one disk and we are asked to optimise for query speed this option is a bad one.
    - Initial cost: `O(1)` Query cost `O(n)`
- Sort the input then binary search on every query
    - This sounds simple but how do we manage this for multiple fields? We would need to sort all the values for each field and binary search on the field values.
    - Initial cost  `O(a * n log(n))` where a is the total number of fields and n is the larger number of values per field` Query cost `O(log(n))`
- Maintain a Binary search tree for each field and search through the tree on every query
    - This is essentially the same as above, we need to maintain a BST for each field's values
    - Initial cost `O(a * n log(n))` Query cost `O(log(n))` on average `O(n^2)` in the worst case when the input is already sorted'
- Prefix/Suffix Trie
    - My favourite family of data structures... but
    - Difficult to implement and a little overkill for our use case since we aren't doing prefix or free text search
    - We would also need include some logic to determine what field a retrieved value came from
    - Suffix tree can be built in `O(n)` (using Ukonnens) and queried for `O(q)` where `q = lenghth of query`

### Application architecture

There are 4 main components within this search application:
- `store`: defines the way data is loaded from a datastore - could be local disk, cloud storage (gcs, s3)
- `model`: defines the objects that will be indexed and searched
- `index`: should take any list of models and index its records
- `db`: should take any store and read from it, define how the specific application will query the indexed models

### Some things I would do given more time
* Testing
  - Include integration tests for the cli prompt
  - Include tests that ensure the inverted index is exactly what we expect it to look like, not just that we can query it correctly (i.e that it doesn't contain records it shouldn't)
  - Using a library like `Faker` to generate mock ticket/user documents
* Refine some of the abstractions between `model` and `db` perhaps adding another layer in between to define `model` interaction behaviour
* Given some more use cases/constraints deal with `model` schemas smarter, perhaps creating more fleshed out `User` and `Ticket` models
