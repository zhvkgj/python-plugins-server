#!/usr/bin/env python3
from pathlib import Path

import yaml

import src.paddle_api_impl.project_pb2 as project_api
import src.paddle_api_impl.project_pb2_grpc as project_servicer
from config import PaddleProjectConfigImpl
from config_spec import PaddleProjectConfigSpecImpl
from converters import to_composite_spec, to_protobuf_composite
from src.paddle_api.config_spec import CompositeSpecNode
from src.paddle_api.plugin import MessageType, ExtendedPaddleProject


class AsyncPaddleApiClient:
    def __init__(self, grpc_channel) -> None:
        self.stub = project_servicer.ProjectStub(grpc_channel)

    async def print_message(self, project_id: str, message: str, type_name: str) -> None:
        await self.stub.PrintMessage(project_api.PrintRequest(
            projectId=project_id, message=message, type=project_api.PrintRequest.Type.Value(type_name))
        )

    async def get_configuration_specification(self, project_id: str) -> CompositeSpecNode:
        return to_composite_spec(await self.stub.GetConfigurationSpecification(
            project_api.GetConfigSpecRequest(projectId=project_id)
        ))

    async def update_configuration_specification(self, project_id: str, config_spec: CompositeSpecNode) -> None:
        await self.stub.UpdateConfigurationSpecification(
            project_api.UpdateConfigSpecRequest(projectId=project_id, configSpec=to_protobuf_composite(config_spec))
        )


class ExtendedPaddleProjectImpl(ExtendedPaddleProject):
    def __init__(self, project_id: str, working_dir: str, grpc_client: AsyncPaddleApiClient) -> None:
        self.__project_id = project_id
        self.__working_dir = working_dir
        self.__paddle_client = grpc_client
        self.__paddle_project_config = None
        self.__paddle_project_config_path = Path(self.__working_dir).resolve().joinpath("paddle.yaml")
        self.reload_config()
        self.__paddle_project_config_spec = PaddleProjectConfigSpecImpl(self.__project_id, self.__paddle_client)

    async def print_message(self, message: str, message_type: MessageType) -> None:
        await self.__paddle_client.print_message(self.__project_id, message, message_type.name)

    @property
    def config_spec(self) -> PaddleProjectConfigSpecImpl:
        return self.__paddle_project_config_spec

    def reset_config_spec(self) -> None:
        self.__paddle_project_config_spec.reset()

    @property
    def config(self) -> PaddleProjectConfigImpl:
        return self.__paddle_project_config

    def reload_config(self) -> None:
        with open(str(self.__paddle_project_config_path), "r") as stream:
            try:
                self.__paddle_project_config = PaddleProjectConfigImpl(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)
