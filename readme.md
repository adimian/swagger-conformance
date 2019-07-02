# swaggercheck

You have a Swagger (aka OpenAPI) schema defining an API you provide - but does your API really conform to that schema, and does it correctly handle all valid inputs?

`swaggercheck` combines the power of `hypothesis` for property based / fuzz testing with `pyswagger` to explore all corners of your API - testing its conformance to its specification.

[![asciicast](https://asciinema.org/a/70ybJ8DqSG5u723GkHe3QMsU5.svg)](https://asciinema.org/a/70ybJ8DqSG5u723GkHe3QMsU5?t=25)


## Swagger-conformance

This project is a fork of [swagger-conformance by Oliver Pratt](http://swagger-conformance.readthedocs.io/en/latest/) and contributors. 

The original library worked fine, but missed several options that were important to me (such as basic authentication support from the command line), so I made an adapted version that is **breaking** the original. 

I don't have plans for the moment contributing my changes upstream since it would be a significant effort to have a nice CLI and a nice embeddable library at the same time.

You *could* use `swaggercheck` as a library, but the purpose of the tool is to have a nice CLI that can output shiny colors in my terminal or in during CI builds, so most design decisions will be tailored towards this goal.

## Purpose

A Swagger/OpenAPI Spec allows you to carefully define what things are and aren't valid for your API to consume and produce. This tool takes that definition, and tries to make requests exploring all parts of the API while strictly adhering to the schema. Its aim is to find any places where your application fails to adhere to its own spec, or even just falls over entirely, so you can fix them up.

_This is not a complete fuzz tester of your HTTP interface e.g. sending complete garbage, or to non-existent endpoints, etc. It's aiming to make sure that any valid client, using your API exactly as you specify, can't break it._

## Installation

    $ pip install swagger-check
    
## Usage

After setup, the simplest test you can run against your API is just the following from the command line:

```bash
swaggercheck 'http://example.com/api/schema.json'
```

where the URL should resolve to your swagger schema, or it can be a path to the file on disk.

## Wait, I don't get it, what does this thing do?

In short, it lets you generate example values for parameters to your Swagger API operations, make API requests using these values, and verify the responses.
