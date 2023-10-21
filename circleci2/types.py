from datetime import datetime
from tracemalloc import stop
from typing import TYPE_CHECKING, Any, Literal, NewType, Optional
from uuid import UUID
from pydantic import BaseModel, Field, model_serializer, model_validator


Branch = NewType("Branch", str)
PageToken = NewType("PageToken", str)
PipelineId = NewType("PipelineId", UUID)
WorkflowId = NewType("WorkflowId", UUID)
UserId = NewType("UserId", UUID)
WorkflowStatus = Literal[
    "success", "running", "not_run", "failed", "error", "failing", "on_hold", "canceled", "unauthorized"
]


class ProjectSlug(BaseModel):
    vcs: str
    organization: str
    repository: str

    @classmethod
    def github(cls, organization: str, repository: str) -> "ProjectSlug":
        return cls(vcs="github", organization=organization, repository=repository)

    @model_serializer
    def serialize_slug(self) -> str:
        return f"{self.vcs}/{self.organization}/{self.repository}"

    def __str__(self) -> str:
        return self.serialize_slug()

    @model_validator(mode="before")
    @classmethod
    def deserialize_slug(cls, data: Any) -> Any:
        if isinstance(data, str):
            split = data.split("/")
            assert len(split) == 3, "Invalid project slug"
            return {"vcs": split[0], "organization": split[1], "repository": split[2]}
        else:
            return data

    if TYPE_CHECKING:
        # Ensure type checkers see the correct return type
        def model_dump(
            self,
            *,
            mode: Literal["json", "python"] | str = "python",
            include: Any = None,
            exclude: Any = None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool = True,
        ) -> str:
            ...


class ProjectPipelinesQueryParams(BaseModel):
    branch: Optional[Branch]
    page_token: Optional[PageToken]


class PipelineWorkflowQueryParams(BaseModel):
    page_token: Optional[PageToken]


class PipelineError(BaseModel):
    type: Literal["config", "config-fetch", "timeout", "permission", "other", "plan"]
    message: str


class TriggerParameters(BaseModel):
    name: Any


class Actor(BaseModel):
    login: str
    avatar_url: str


class Trigger(BaseModel):
    type: Literal["scheduled_pipeline", "explicit", "api", "webhook"]
    received_at: datetime
    actor: Actor


class Commit(BaseModel):
    subject: str
    body: str


class PipelineVCS(BaseModel):
    provider_name: str
    target_repository_url: str
    origin_repository_url: str
    branch: Optional[str] = Field(default=None)
    review_id: Optional[str] = Field(default=None)
    review_url: Optional[str] = Field(default=None)
    revision: str
    tag: Optional[str] = Field(default=None)
    commit: Optional[Commit] = Field(default=None)


class Pipeline(BaseModel):
    id: PipelineId
    errors: list[PipelineError]
    project_slug: ProjectSlug
    updated_at: Optional[datetime] = Field(default=None)
    number: int
    state: Literal["created", "errored", "setup-pending", "setup", "pending"]
    created_at: datetime
    trigger_parameters: Optional[TriggerParameters] = Field(default=None)
    trigger: Trigger
    vcs: PipelineVCS


class ProjectPipelineResponse(BaseModel):
    next_page_token: Optional[PageToken] = Field(default=None)
    items: list[Pipeline]


class Workflow(BaseModel):
    id: WorkflowId
    pipeline_id: PipelineId
    canceled_by: Optional[UserId] = Field(default=None)
    errored_by: Optional[UserId] = Field(default=None)
    name: str
    project_slug: ProjectSlug
    tag: Optional[str] = Field(default=None)
    status: WorkflowStatus
    started_by: UserId
    pipeline_number: int
    created_at: datetime
    stopped_at: datetime

    @property
    def ended(self) -> bool:
        return self.status in {"success", "failed", "error", "canceled", "unauthorized"}


class PipelineWorkflowResponse(BaseModel):
    next_page_token: Optional[PageToken] = Field(default=None)
    items: list[Workflow]
