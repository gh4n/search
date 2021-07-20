The project implements a simple search to find tickets and users by field.

Some things I could do given more time
* testing
  - include integration tests for the cli prompt
  - include tests around users having the correct tickets and tickets having the correct assignee
  - include tests that ensure the inverted index is exactly what we expect it to look like, not just that we can query it correctly
  - using a library like faker to generate mock ticket/user documents
* 
Assumptions
- I have inferred the user and ticket schemas from the example files, this solution requires a hardcoded schema definition. Initially when I wrote this I included a method to generate the schema for a set of records by finding the superset of columns present in all fields. I decided for simplicity's sake to omit this.
- The relationship between user and ticket is defined by user._id == ticket.assignee_id

----------
Application architecture

There are 4 main components within this search application:
1. store: define the way data is loaded from a datastore - could be local disk, cloud storage (gcs, s3)
2. model: define the objects that will be indexed and searched
3. index: should take any model and index it
4. db: should take any store and read from it and define how the specific application will query the indexed models

----------

How do I run it?

Navigate the root of the directory build and tag the docker container

- docker build -t zensearch .
- docker run -it zensearch

----------

How does the search work?

An inverted index is constructed from each field and value of the input corpus. Consider the document below with id: 1

{
  "name": "saskia",
  "age": 1,
  "noises": [
    "meow",
    "purr",
    "sniff"
  ],
  "temperament": "agreeable",
  "coat": "short"
}

would look like this when indexed - each field and value key the document with those attributes

{
  "name" : {
    "saskia": ["1"]
  },
  "age": {
    "1": ["1"]
  },
  "noises": {
    "meow": ["1"],
    "purr": ["1"],
    "sniff": ["1"]
  },
  "temperament": {
    "agreeable": ["1"]
  },
  "coat": {
    "short": [1]
  }
}

Let's add another document with id: 2

{   
    name: bo,
    age: 1,
    noises: [
        rawr,
        purr,
        yawn,
        meow
    ]
    temperament: skittish,
    coat: long
}

Now the index looks like this

{
    name : {
        saskia: [1]
        bo: [2]
    },
    age: {
        1: [1, 2]
    },
    noises: {
        meow: [1, 2],
        purr: [1, 2],
        sniff: [1],
        rawr: [2],
        yawn: [2],
    },
    temperament: {
        agreeable: [1],
        skittish: [2]
    },
    coat: {
        short: [1]
        long: [2]
    }
}

If we want to find all the cats who purr we simple return index[noises][purr] and we get documents 1 and 2. If we want to find all cats named saskia we return index[name][saskia] and we get document 1.
