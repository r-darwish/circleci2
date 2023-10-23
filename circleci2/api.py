import requests
from requests.auth import HTTPBasicAuth

from typing import Generator, Optional, Type

from pydantic import BaseModel
from circleci2.types import (
    CircleResponse,
    Job,
    Pipeline,
    PipelineWorkflowResponse,
    ResponseItem,
    MultiPageQueryParams,
    MultipageResponse,
    PipelineWorkflowQueryParams,
    ProjectPipelinesQueryParams,
    PipelineId,
    ProjectSlug,
    Branch,
    PageToken,
    ProjectPipelineResponse,
    Workflow,
    WorkflowId,
    WorkflowJobsQueryParams,
    WorkflowJobsResponse,
)


class API:
    def __init__(self, token: str):
        self._token = token
        self._client = requests.Session()

    def _request(
        self, endpoint: str, *, query_params: BaseModel, response_type: Type[CircleResponse]
    ) -> CircleResponse:
        response = self._client.get(
            "https://circleci.com/api/v2/" + endpoint,
            params=query_params.model_dump(),
            auth=HTTPBasicAuth(self._token, ""),
            headers={"content-type": "application/json"},
        )

        response.raise_for_status()
        return response_type.model_validate_json(response.text)

    def _multipage_request(
        self, endpoint: str, *, query_params: MultiPageQueryParams, response_type: Type[ResponseItem]
    ) -> Generator[ResponseItem, None, None]:
        while True:
            data = self._request(endpoint, query_params=query_params, response_type=MultipageResponse[response_type])
            yield from data.items
            if data.next_page_token is None:
                break

            query_params.page_token = data.next_page_token

    def get_project_pipelines(
        self, project: ProjectSlug, *, branch: Optional[Branch] = None, page_token: Optional[PageToken] = None
    ) -> ProjectPipelineResponse:
        return self._request(
            f"project/{project.serialize_slug()}/pipeline",
            query_params=ProjectPipelinesQueryParams(branch=branch, page_token=page_token),
            response_type=ProjectPipelineResponse,
        )

    def iter_project_pipelines(
        self, project: ProjectSlug, *, branch: Optional[Branch] = None
    ) -> Generator[Pipeline, None, None]:
        return self._multipage_request(
            f"project/{project.serialize_slug()}/pipeline",
            query_params=ProjectPipelinesQueryParams(branch=branch, page_token=None),
            response_type=Pipeline,
        )

    def get_pipline_workflows(
        self, pipeline_id: PipelineId, *, page_token: Optional[PageToken] = None
    ) -> PipelineWorkflowResponse:
        return self._request(
            f"pipeline/{pipeline_id}/workflow",
            query_params=PipelineWorkflowQueryParams(page_token=page_token),
            response_type=PipelineWorkflowResponse,
        )

    def iter_pipline_workflows(self, pipeline_id: PipelineId) -> Generator[Workflow, None, None]:
        return self._multipage_request(
            f"pipeline/{pipeline_id}/workflow",
            query_params=PipelineWorkflowQueryParams(page_token=None),
            response_type=Workflow,
        )

    def get_workflow_jobs(
        self, workflow_id: WorkflowId, *, page_token: Optional[PageToken] = None
    ) -> WorkflowJobsResponse:
        return self._request(
            f"workflow/{workflow_id}/job",
            query_params=WorkflowJobsQueryParams(page_token=page_token),
            response_type=WorkflowJobsResponse,
        )

    def iter_workflow_jobs(self, workflow_id: WorkflowId) -> Generator[Job, None, None]:
        return self._multipage_request(
            f"workflow/{workflow_id}/job",
            query_params=WorkflowJobsQueryParams(page_token=None),
            response_type=Job,
        )
