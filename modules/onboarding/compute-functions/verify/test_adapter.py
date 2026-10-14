import asyncio
import importlib
import json
from contextlib import asynccontextmanager

import azure.functions as func

import app as api_module
import function_app as entry_module


def fresh_entry():
    importlib.reload(api_module)
    return importlib.reload(entry_module).app


@asynccontextmanager
async def running_adapter(entry):
    handler = entry.get_functions()[0].get_user_function()
    try:
        yield handler
    finally:
        if entry.startup_task_done:
            await entry.middleware.notify_shutdown()


async def request(handler, method, path, payload=None):
    body = b"" if payload is None else json.dumps(payload).encode()
    req = func.HttpRequest(
        method=method,
        url=f"http://localhost{path}",
        headers={"Content-Type": "application/json"},
        params={},
        route_params={},
        body=body,
    )
    return await handler(req, None)


def decoded(response):
    return json.loads(response.get_body())


def test_adapter_health_write_read_and_validation():
    entry = fresh_entry()

    async def journey():
        async with running_adapter(entry) as handler:
            health = await request(handler, "GET", "/health")
            assert health.status_code == 200
            assert decoded(health) == {"status": "ok"}
            initial = await request(handler, "GET", "/items")
            assert len(decoded(initial)) == 2
            created = await request(handler, "POST", "/items", {"name": " adapter-item "})
            assert created.status_code == 201
            assert decoded(created) == {"id": 3, "name": "adapter-item"}
            after = await request(handler, "GET", "/items")
            assert len(decoded(after)) == 3
            assert decoded(after)[-1] == decoded(created)
            invalid = await request(handler, "POST", "/items", {"name": ""})
            assert invalid.status_code == 422
            unchanged = await request(handler, "GET", "/items")
            assert decoded(unchanged) == decoded(after)
            missing = await request(handler, "GET", "/not-a-route")
            assert missing.status_code == 404

    asyncio.run(journey())


def test_adapter_state_is_reset_by_fresh_application():
    first_entry = fresh_entry()
    second_entry = fresh_entry()

    async def journey():
        async with running_adapter(first_entry) as first:
            created = await request(first, "POST", "/items", {"name": "temporary"})
            assert created.status_code == 201
            assert len(decoded(await request(first, "GET", "/items"))) == 3
        async with running_adapter(second_entry) as second:
            assert len(decoded(await request(second, "GET", "/items"))) == 2

    asyncio.run(journey())


def test_adapter_declares_function_auth_and_catch_all_route():
    functions = fresh_entry().get_functions()
    assert len(functions) == 1
    trigger = next(
        binding.get_dict_repr()
        for binding in functions[0].get_bindings()
        if binding.get_dict_repr()["type"] == "httpTrigger"
    )
    assert trigger["authLevel"] == func.AuthLevel.FUNCTION
    assert trigger["route"] == "/{*route}"
    assert func.HttpMethod.GET in trigger["methods"]
    assert func.HttpMethod.POST in trigger["methods"]
