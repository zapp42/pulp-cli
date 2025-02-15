from typing import Any, List, Optional

from pulpcore.cli.common.context import (
    EntityDefinition,
    PluginRequirement,
    PulpContentContext,
    PulpEntityContext,
    PulpRemoteContext,
    PulpRepositoryContext,
    PulpRepositoryVersionContext,
    registered_repository_contexts,
)
from pulpcore.cli.common.i18n import get_translation

translation = get_translation(__name__)
_ = translation.gettext


class PulpContainerBlobContext(PulpContentContext):
    ENTITY = _("container blob")
    ENTITIES = _("container blobs")
    HREF = "container_blob_href"
    ID_PREFIX = "content_container_blobs"


class PulpContainerManifestContext(PulpContentContext):
    ENTITY = _("container manifest")
    ENTITIES = _("container manifests")
    HREF = "container_manifest_href"
    ID_PREFIX = "content_container_manifests"


class PulpContainerTagContext(PulpContentContext):
    ENTITY = _("container tag")
    ENTITIES = _("container tags")
    HREF = "container_tag_href"
    ID_PREFIX = "content_container_tags"


class PulpContainerNamespaceContext(PulpEntityContext):
    ENTITY = _("container namespace")
    ENTITIES = _("container namespaces")
    HREF = "container_container_namespace_href"
    ID_PREFIX = "pulp_container_namespaces"
    CAPABILITIES = {"roles": [PluginRequirement("container", "2.11.0.dev")]}


class PulpContainerDistributionContext(PulpEntityContext):
    ENTITY = _("container distribution")
    ENTITIES = _("container distributions")
    HREF = "container_container_distribution_href"
    ID_PREFIX = "distributions_container_container"
    NULLABLES = {"repository_version", "repository"}
    CAPABILITIES = {"roles": [PluginRequirement("container", "2.11.0.dev")]}

    def preprocess_body(self, body: EntityDefinition) -> EntityDefinition:
        body = super().preprocess_body(body)
        version = body.pop("version", None)
        if version is not None:
            repository_href = body.pop("repository")
            body["repository_version"] = f"{repository_href}versions/{version}/"
        return body


class PulpContainerRemoteContext(PulpRemoteContext):
    ENTITY = _("container remote")
    ENTITIES = _("container remotes")
    HREF = "container_container_remote_href"
    ID_PREFIX = "remotes_container_container"
    NULLABLES = PulpRemoteContext.NULLABLES | {"include_tags", "exclude_tags"}
    CAPABILITIES = {"roles": [PluginRequirement("container", "2.11.0.dev")]}


class PulpContainerRepositoryVersionContext(PulpRepositoryVersionContext):
    HREF = "container_container_repository_version_href"
    ID_PREFIX = "repositories_container_container_versions"


class PulpContainerPushRepositoryVersionContext(PulpRepositoryVersionContext):
    HREF = "container_container_push_repository_version_href"
    ID_PREFIX = "repositories_container_container_push_versions"


class PulpContainerBaseRepositoryContext(PulpRepositoryContext):
    def tag(self, tag: str, digest: str) -> Any:
        self.needs_capability("tag")
        return self.call(
            "tag",
            parameters={self.HREF: self.pulp_href},
            body={"tag": tag, "digest": digest},
        )

    def untag(self, tag: str) -> Any:
        self.needs_capability("tag")
        return self.call(
            "untag",
            parameters={self.HREF: self.pulp_href},
            body={"tag": tag},
        )


class PulpContainerRepositoryContext(PulpContainerBaseRepositoryContext):
    HREF = "container_container_repository_href"
    ID_PREFIX = "repositories_container_container"
    VERSION_CONTEXT = PulpContainerRepositoryVersionContext
    CAPABILITIES = {
        "sync": [PluginRequirement("container")],
        "pulpexport": [PluginRequirement("container", "2.8.0.dev")],
        "tag": [PluginRequirement("container", "2.3.0")],
        "roles": [PluginRequirement("container", "2.11.0.dev")],
    }

    def modify(
        self,
        href: str,
        add_content: Optional[List[str]] = None,
        remove_content: Optional[List[str]] = None,
        base_version: Optional[str] = None,
    ) -> Any:
        if remove_content:
            self.call(
                "remove", parameters={self.HREF: href}, body={"content_units": remove_content}
            )
        if add_content:
            self.call("add", parameters={self.HREF: href}, body={"content_units": add_content})

    def copy_tag(self, source_href: str, tags: Optional[List[str]]) -> Any:
        body = {"source_repository_version": source_href, "names": tags}
        body = self.preprocess_body(body)
        return self.call("copy_tags", parameters={self.HREF: self.pulp_href}, body=body)

    def copy_manifest(
        self,
        source_href: str,
        digests: Optional[List[str]],
        media_types: Optional[List[str]],
    ) -> Any:
        body = {
            "source_repository_version": source_href,
            "digests": digests,
            "media_types": media_types,
        }
        body = self.preprocess_body(body)
        return self.call("copy_manifests", parameters={self.HREF: self.pulp_href}, body=body)


class PulpContainerPushRepositoryContext(PulpContainerBaseRepositoryContext):
    HREF = "container_container_push_repository_href"
    ID_PREFIX = "repositories_container_container_push"
    VERSION_CONTEXT = PulpContainerPushRepositoryVersionContext
    CAPABILITIES = {
        "tag": [PluginRequirement("container", "2.3.0")],
        "roles": [PluginRequirement("container", "2.11.0.dev")],
    }


registered_repository_contexts["container:container"] = PulpContainerRepositoryContext
registered_repository_contexts["container:push"] = PulpContainerPushRepositoryContext
