import json
import time

from fastapi import HTTPException
from ..Database.database import inventory_collection,product_collection
from ..Models.models import Inventory
from ..Models.models import User
from ..Database.database import redis_client

class inventoryService:

    def addNewInventory(inventory : Inventory, current_user : User):
        if current_user["user_role"] == "manager":
            getExistingInventoryId=inventory_collection.find_one({
                "inventory_id" : inventory.inventory_id
            })
            getProductId=product_collection.find_one({
                "product_id":inventory.product_id
            })
            if getExistingInventoryId is None:
                if getProductId is not None:
                    inventory_collection.insert_one(inventory.model_dump())
                    return{
                        "Message" : "New inventory added",
                        "Inventory" : inventory
                    }
                else:
                    raise HTTPException(status_code=404,detail="Product not found")

            else:
                raise HTTPException(status_code=409,detail="Inventory already in the cart")
        else:
            raise HTTPException(status_code=401,detail="Only managers can add the inventories")


    async def getSingleInventory(id: str, current_user: User):

        cache_key = f"inventory:{id}"

        if current_user["user_role"] != "manager":
            raise HTTPException(
                status_code=401,
                detail="Only managers can see the inventories"
            )

        start_time = time.perf_counter()

        # 1. Check Redis
        cached_inventory = await redis_client.get(cache_key)

        if cached_inventory is not None:

            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000

            return {
                "source": "Redis",
                "inventory": json.loads(cached_inventory),
                "execution_time_ms": round(execution_time, 2)
            }

        # 2. Cache miss → MongoDB
        inventory = inventory_collection.find_one(
            {"inventory_id": id}
        )

        if inventory is None:
            raise HTTPException(
                status_code=404,
                detail="Inventory not found"
            )

        # Convert ObjectId
        inventory["_id"] = str(inventory["_id"])

        # 3. Store in Redis
        await redis_client.set(
            cache_key,
            json.dumps(inventory),
            ex=300
        )

        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000

        return {
            "source": "MongoDB",
            "inventory": inventory,
            "execution_time_ms": round(execution_time, 2)
        }
        
    async def getAllInventories(current_user : User):
        if current_user["user_role"] == "manager":
            inventories = []
            for inventory in inventory_collection.find({}):
                inventory["_id"] = str(inventory["_id"])
                inventories.append(inventory)
            return inventories
        else:
            raise HTTPException(status_code=401,detail="Only managers can see the inventories")

    async def updateSingleInventory(id:str,updateInventory:Inventory):
        inventory = inventory_collection.update_one(
            {"inventory_id" : id},
            {"$set" : updateInventory.model_dump()}
        )

        if inventory.modified_count == 0:
            raise HTTPException(status_code=200,detail="No data updated")
        else:
            return {
                "Message":"Data updated",
                "Updated Inventory":updateInventory
            }

    async def deleteSingleInventory(id:str,current_user:User):
        if current_user["user_role"] == "manager":
            result = inventory_collection.delete_one({
                "inventory_id":id
            })
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Inventory not found"
                )
            else:
                return{"message":"Inventory deleted"}
        
        else:
            return HTTPException(
                status_code=401,
                detail="Only managers can delete the inventory"
            )
        
