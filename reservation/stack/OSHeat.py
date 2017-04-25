from heatclient import client as HClient
from .OSTools import  OSTools


class OSHeat():

    def __init__(self, **kwargs):
        self.session = kwargs.get("session")
        self.client = HClient.Client("1", session=self.session)

    def list(self):
        """List available stacks
        Returns:
            List of stacks object
            list
        """
        return list(self.client.stacks.list())

    def create(self, name, template):

        return self.client.stacks.create({
            "files": {},
            "disable_rollback": "true",
            "stack_name": name,
            "template": template,
            "timeout_mins": 30
        })

    def preview(self, name, flavor, template):

        return self.client.stacks.create({
            "files": {},
            "disable_rollback": "true",
            "parameters": {
                "flavor": flavor
            },
            "stack_name": name,
            "template": template,
            "timeout_mins": 30
        })

    def delete(self, name):
        """Delete image
        Args:
            image: Name or id - this will be detected
        Returns:
            Status of operation
            bool
        """
        if not OSTools.isID(name):
            findRes = self.find(name=name)
            if findRes and len(findRes) > 0:
                name = findRes[0]
        imageObj = self.find(image_id=name.id)
        if imageObj:
            imageObj.delete()
            return True
        else:
            return False

    def find(self, **kwargs):
        """Find items
        Find items based on arguments:
        - name
        - item ID
        Args:
            name: Name to search for (default: {None})
            item_id: Item ID to search for (default: {None})
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
