# CircleCI 2

CircleCI v2 API wrapper with type annotations.

Example:

```python
circle = circleci2.API(os.environ["CIRCLE_TOKEN"])
for pipeline in circle.iter_project_pipelines(circleci2.ProjectSlug.github("r-darwish", "circle2")):
    for workflow in circle.iter_pipline_workflows(pipeline.id):
        print(workflow.name)
```
