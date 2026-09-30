from fastapi import APIRouter,Body, Depends
from app.Services import userService
from ..Database.database import inventory_collection
from ..Models.models import (Inventory,Orders)
from ..Services.inventoryService import inventoryService
from ..Services.userService import userService
from ..Services.orderService import orderService

class inventoryRoute:

    inventoryRouter=APIRouter()

    @inventoryRouter.post("/inventory",status_code=201)
    def addNewInventory(inventory:Inventory,current_user=Depends(userService.getCurrentUser)):
        return inventoryService.addNewInventory(inventory,current_user)

    @inventoryRouter.get("/inventory",status_code=200)
    async def getAllInventories(current_user=Depends(userService.getCurrentUser)):
        return await inventoryService.getAllInventories(current_user)

    @inventoryRouter.get("/inventory/{id}",status_code=200)
    async def getSingleInventory(id : str,current_user=Depends(userService.getCurrentUser)):
        return await inventoryService.getSingleInventory(id,current_user)

    @inventoryRouter.put("/inventory/{id}")
    async def updateSingleInventory(id:str,updateInventory:Inventory):
        return await inventoryService.updateSingleInventory(id,updateInventory)

    @inventoryRouter.delete("/inventory/{id}",status_code=200)
    async def deleteSingleInventory(id:str,current_user=Depends(userService.getCurrentUser)):
        return await inventoryService.deleteSingleInventory(id,current_user)

    
