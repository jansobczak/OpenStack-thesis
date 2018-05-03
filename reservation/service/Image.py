class Image:

    name = None
    checksum = None
    container_fromat = None
    created_at = None
    disk_format = None
    file = None
    id = None
    is_public = None
    min_disk = None
    min_ram = None
    owner = None
    protected = None
    schema = None
    size = None
    status = None
    tags = None
    updated_at = None
    virtal_size = None
    visibility = None


    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.checksum = kwargs.get("checksum")
        self.container_format = kwargs.get("container_format")
        self.created_at = kwargs.get("created_at")
        self.disk_format = kwargs.get("disk_format")
        self.file = kwargs.get("file")
        self.id = kwargs.get("id")
        self.is_public = kwargs.get("is_public")
        self.min_disk = kwargs.get("min_disk")
        self.min_ram = kwargs.get("min_ram")
        self.owner = kwargs.get("owner")
        self.protected = kwargs.get("protected")
        self.schema = kwargs.get("schema")
        self.size = kwargs.get("size")
        self.status = kwargs.get("status")
        self.tags = kwargs.get("tags")
        self.updated_at = kwargs.get("updated_at")
        self.virtual_size = kwargs.get("virtual_size")
        self.visibility = kwargs.get("visibility")


    def parseDict(self, data):
        if data is not None:
            if "checksum" in data:
                self.checksum = data["checksum"]
            if "container_format" in data:
                self.container_format = data["container_format"]
            if "created_at" in data:
                self.created_at = data["created_at"]
            if "disk_format" in data:
                self.disk_format = data["disk_format"]
            if "file" in data:
                self.file = data["file"]
            if "id" in data:
                self.id = data["id"]
            if "is_public" in data:
                self.is_public = data["is_public"]
            if "min_disk" in data:
                self.min_disk = data["min_disk"]
            if "min_ram" in data:
                self.min_ram = data["min_ram"]
            if "name" in data:
                self.name = data["name"]
            if "owner" in data:
                self.owner = data["owner"]
            if "protected" in data:
                self.protected = data["protected"]
            if "schema" in data:
                self.schema = data["schema"]
            if "size" in data:
                self.size = data["size"]
            if "status" in data:
                self.status = data["status"]
            if "tags" in data:
                self.tags = data["tags"]
            if "updated_at" in data:
                self.updated_at = data["updated_at"]
            if "virtual_size" in data:
                self.virtual_size = data["virtual_size"]
            if "visibility" in data:
                self.visibility = data["visibility"]
            return self
        else:
            return None

    def parseJSON(self, data):
        if "image" in data:
            if "checksum" in data[image]:
                self.checksum = data[image]["checksum"]
            if "container_format" in data[image]:
                self.container_format = data[image]["container_format"]
            if "created_at" in data[image]:
                self.created_at = data[image]["created_at"]
            if "disk_format" in data[image]:
                self.disk_format = data[image]["disk_format"]
            if "file" in data[image]:
                self.file = data[image]["file"]
            if "id" in data[image]:
                self.id = data[image]["id"]
            if "is_public" in data[image]:
                self.is_public = data[image]["is_public"]
            if "min_disk" in data[image]:
                self.min_disk = data[image]["min_disk"]
            if "min_ram" in data[image]:
                self.min_ram = data[image]["min_ram"]
            if "name" in data[image]:
                self.name = data[image]["name"]
            if "owner" in data[image]:
                self.owner = data[image]["owner"]
            if "protected" in data[image]:
                self.protected = data[image]["protected"]
            if "schema" in data[image]:
                self.schema = data[image]["schema"]
            if "size" in data[image]:
                self.size = data[image]["size"]
            if "status" in data[image]:
                self.status = data[image]["status"]
            if "tags" in data[image]:
                self.tags = data[image]["tags"]
            if "updated_at" in data[image]:
                self.updated_at = data[image]["updated_at"]
            if "virtual_size" in data[image]:
                self.virtual_size = data[image]["virtual_size"]
            if "visibility" in data[image]:
                self.visibility = data[image]["visibility"]
            return self
        else:
            return None

    def to_dict(self):
        return dict(checksum=self.checksum, container_format=self.container_format, created_at=self.created_at, disk_format=self.disk_format, file=self.file, id=self.id, is_public=self.is_public, min_disk=self.min_disk, min_ram=self.min_ram, name=self.name, owner=self.owner, protected=self.protected, schema=self.schema, size=self.size, status=self.status, tags=self.tags, updated_at=self.updated_at, virtual_size=self.virtual_size, visibility=self.visibility)