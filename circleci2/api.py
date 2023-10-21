import requests
from requests.auth import HTTPBasicAuth

from typing import Optional

from pydantic import BaseModel
from circleci2.types import (
    Pipeline,
    PipelineWorkflowQueryParams,
    PipelineWorkflowResponse,
    ProjectPipelinesQueryParams,
    PipelineId,
    ProjectSlug,
    Branch,
    PageToken,
    ProjectPipelineResponse,
    WorkflowStatus,
)


class API:
    def __init__(self, token: str):
        self._token = token
        self._client = requests.Session()

    def _request(self, endpoint: str, *, query_params: BaseModel) -> str:
        response = self._client.get(
            "https://circleci.com/api/v2/" + endpoint,
            params=query_params.model_dump(),
            auth=HTTPBasicAuth(self._token, ""),
            headers={"content-type": "application/json"},
        )
        response.raise_for_status()
        return response.text

    def get_project_pipelines(
        self, project: ProjectSlug, *, branch: Optional[Branch] = None, page_token: Optional[PageToken] = None
    ) -> ProjectPipelineResponse:
        data = self._request(
            f"project/{project.serialize_slug()}/pipeline",
            query_params=ProjectPipelinesQueryParams(branch=branch, page_token=page_token),
        )
        return ProjectPipelineResponse.model_validate_json(data)

    def get_pipline_workflows(
        self, pipeline_id: PipelineId, *, page_token: Optional[PageToken] = None
    ) -> PipelineWorkflowResponse:
        data = self._request(
            f"pipeline/{pipeline_id}/workflow",
            query_params=PipelineWorkflowQueryParams(page_token=page_token),
        )
        return PipelineWorkflowResponse.model_validate_json(data)
