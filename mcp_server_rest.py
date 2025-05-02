from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import sys, os , json
from dotenv import load_dotenv
import uuid
import logging
import time

logging.basicConfig(
    filename='/home/admin/app.log',                # Log file name
    level=logging.INFO,                # Minimum log level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log message format
)

logging.info('Starting the FastMCP server...')

# Initialize FastMCP server
mcp = FastMCP("CVP MCP Server")

#async function to return creds
async def get_env_vars():
    load_dotenv()
    cvp = os.environ.get("CVP")
    cvtoken = os.environ.get("CVPTOKEN")
    datadict = {}
    datadict['cvtoken'] = cvtoken
    datadict["cvp"] = cvp
    print (datadict, file=sys.stderr) # Debug print
    return datadict

#Function to fetch data get request wise from CVP.
async def get_request_cvp(token: str, url: str) -> dict[str, Any] | None:
    headers = {
        "Accept": "application/json"
    }
    cookies = {
        "access_token": token
    }

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(url, headers=headers, cookies=cookies)
            response.raise_for_status()
        except httpx.RequestError as exc:
            print(f"Request failed: {exc}", file=sys.stderr)
            sys.exit(1)

    parsed_objects = []
    for line in response.text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            parsed_objects.append(obj)
        except json.JSONDecodeError as e:
            print(f"Failed to parse line:\n{line}\nError: {e}", file=sys.stderr)

    headers = {
        "Accept": "application/geo+json"
    }
    cookies = {
        "access_token": token
    }
    parsed_objects = []
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0, cookies=cookies)
            response.raise_for_status()
            if response.status_code == 204:
                print("Received empty response (204 No Content) from SuzieQ API for")
        except Exception:
            return None
    for line in response.text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            parsed_objects.append(obj)
        except json.JSONDecodeError as e:
            print(f"Failed to parse line:\n{line}\nError: {e}", file=sys.stderr)

    return(parsed_objects)

# Functio to post data to CVP
async def post_request_cvp(token: str, url: str, data: dict[str, Any]) -> dict[str, Any] | None:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    cookies = {
        "access_token": token
    }

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(url, headers=headers, cookies=cookies, json=data)
            response.raise_for_status()
        except httpx.RequestError as exc:
            print(f"Request failed: {exc}", file=sys.stderr)
            sys.exit(1)

    return response.json()

#Get inventory tool returns inventory
@mcp.tool()
async def get_inventory() -> str:
    """Gets the inventory of devices from CVP"""
    cvdata = await get_env_vars()
    print(cvdata, file=sys.stderr)
    cvtoken = cvdata["cvtoken"]
    cvp = cvdata["cvp"]
    devices = await get_request_cvp(cvtoken, f"https://{cvp}/api/resources/inventory/v1/Device/all")
    try:
        return json.dumps(devices, indent=2)
    except TypeError as e:
        error_message = f"Had an issue response to JSON: {str(e)}"
        print(f"[ERROR] {error_message}", file=sys.stderr) # Debug print
        return json.dumps({"error": error_message})

#Get events returns all the events from CVP
@mcp.tool()
async def get_events() -> str:
    """Gets All of the events from CVP"""
    cvdata = await get_env_vars()
    cvtoken = cvdata["cvtoken"]
    cvp = cvdata["cvp"]
    events = await get_request_cvp(cvtoken, f"https://{cvp}/api/resources/event/v1/Event/all")
    try:
        return json.dumps(events, indent=2)
    except TypeError as e:
        error_message = f"Had an issue response to JSON: {str(e)}"
        print(f"[ERROR] {error_message}") # Debug print
        return json.dumps({"error": error_message})


#Get connectivity monitor returns all the connectivity related data from CVP such as jitter, latency, packet loss and http response time
@mcp.tool()
async def get_connectivity_monitor() -> str:
    """Gets All of the Connectivity Monitor data from CVP"""
    cvdata = await get_env_vars()
    cvtoken = cvdata["cvtoken"]
    cvp = cvdata["cvp"]
    events = await get_request_cvp(cvtoken, f"https://{cvp}/api/resources/connectivitymonitor/v1/ProbeStats/all")
    try:
        return json.dumps(events, indent=2)
    except TypeError as e:
        error_message = f"Had an issue response to JSON: {str(e)}"
        print(f"[ERROR] {error_message}") # Debug print
        return json.dumps({"error": error_message})

# create a tag
@mcp.tool()
async def create_tag(tag_name: str, tag_value: str) -> str:
    """Creates a tag in CVP"""
    cvdata = await get_env_vars()
    cvtoken = cvdata["cvtoken"]
    cvp = cvdata["cvp"]
    url = f"https://{cvp}/api/resources/tag/v2/TagConfig"


    ws = f"https://{cvp}/api/resources/workspace/v1/WorkspaceConfig"
    workspace_name = str(uuid.uuid4())
    ws_data = {
        "key": {
            "workspaceId": workspace_name
        },
        "displayName": workspace_name[0:8] + "API demo",
        "description": "API demo"
    }
    ws_build = {
        "key": {
            "workspaceId": workspace_name
        },
        "displayName": workspace_name[0:8] + "API demo",
        "description": "API demo",
        "request": "REQUEST_START_BUILD",
        "requestParams": {
            "requestId": str(uuid.uuid4())
        }
    }
    ws_submit = {
        "key": {
            "workspaceId": workspace_name
        },
        "displayName": workspace_name[0:8] + "API demo",
        "description": "API demo",
        "request": "REQUEST_SUBMIT",
        "requestParams": {
            "requestId": str(uuid.uuid4())
        }
    }
    data = {
        "key":{
            "workspace_id": workspace_name,
            "element_type": "ELEMENT_TYPE_DEVICE",
            "label":tag_name,
            "value":tag_value
        }
    }


    try:
        create_ws = await post_request_cvp(cvtoken, ws, ws_data)
        print(f"Workspace created: {create_ws}", file=sys.stderr) # Debug print
        response = await post_request_cvp(cvtoken, url, data)
        build_ws = await post_request_cvp(cvtoken, ws, ws_build)
        print(f"Workspace build: {build_ws}", file=sys.stderr) # Debug print
        logging.info(f"Workspace build: {build_ws}")
        time.sleep(10)
        submit_ws = await post_request_cvp(cvtoken, ws, ws_submit)
        print(f"Workspace submitted: {submit_ws}", file=sys.stderr) # Debug print
        logging.info(f"Workspace submitted: {submit_ws}")
        return json.dumps(submit_ws, indent=2)
    except TypeError as e:
        error_message = f"Had an issue response to JSON: {str(e)}"
        print(f"[ERROR] {error_message}")
