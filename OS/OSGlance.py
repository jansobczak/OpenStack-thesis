from glanceclient import Client
from OS import OSTools
import time


class OSGlance:
    client = None

    def __init__(self, endpoint, token):
        self.client = Client('1', endpoint=endpoint, token=token)

    def list(self):
        """List avaible images
        Returns:
            List of images object
            list
        """
        generator = self.client.images.list()
        return list(generator)

    def create(self, name, containerFormat, diskFormat, isPublic, pathFile):
        """Create and upload image
        This create image with:
            -containerFormat = ami, ari, aki, bare, ovf, ova, or docker.
            -diskFormat = ami, ari, aki, vhd, vhdx, vmdk, raw, qcow2, vdi, or iso.
        Args:
            name: Name of image
            containerFormat: Container format
            diskFormat: Disk format
            isPublic: Bool value
            pathFile: Path to file
        Returns:
            Image object
        """
        if isPublic:
            isPublic = "public"
        else:
            isPublic = "private"

        image = self.client.images.create(name=name, container_format=containerFormat, disk_format=diskFormat, is_public=isPublic)
        imageId = image.id
        image.update(data=open(pathFile, 'rb'))
        while image.status == "queued":
            image = self.find(image_id=imageId)
            time.sleep(1)
        return self.find(image_id=imageId)

    def delete(self, image):
        """Delete image
        Args:
            image: Name or id - this will be detected
        Returns:
            Status of operation
            bool
        """
        if not OSTools.OSTools.isNeutronID(image):
            findRes = self.find(name=image)
            if findRes and len(findRes) > 0:
                image = findRes[0]
        imageObj = self.find(image_id=image.id)
        if imageObj:
            imageObj.delete()
            return True
        else:
            return False

    def find(self, **kwargs):
        """Find items
        Find items based on arguments:
        - name
        - project ID
        - item ID
        Args:
            name: Name to search for (default: {None})
            item_id: Item ID to search for (default: {None})
            project_id: Project ID  (default: {None})
        Returns:
            One items or array of items
            One item if item_id only
            Array of items if project_id or name
            Mixed
        """
        name = kwargs.get("name")
        item_id = kwargs.get("image_id")
        items = self.list()
        if item_id is not None:
            for item in items:
                if item.id == item_id:
                    return item

        if name is not None:
            returnArray = []
            for item in items:
                if item.name == name:
                    returnArray.append(item)
            return returnArray
        else:
            return None
