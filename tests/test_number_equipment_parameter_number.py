import logging
from lennoxs30api.s30api_async import (
    lennox_system,
)
from custom_components.lennoxs30 import (
    DS_CONNECTED,
    DS_RETRY_WAIT,
    Manager,
)
import pytest
from custom_components.lennoxs30.const import (
    LENNOX_DOMAIN,
    UNIQUE_ID_SUFFIX_EQ_PARAM_NUMBER,
)
from lennoxs30api.s30exception import S30Exception
from homeassistant.exceptions import HomeAssistantError
from custom_components.lennoxs30.number import (
    EquipmentParameterNumber,
)

from homeassistant.const import (
    TEMP_FAHRENHEIT,
)

from unittest.mock import patch

from tests.conftest import conftest_parameter_extra_attributes


@pytest.mark.asyncio
async def test_equipment_parameter_number_unique_id(hass, manager: Manager, caplog):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)
    assert c.unique_id == (
        f"{system.unique_id()}_{UNIQUE_ID_SUFFIX_EQ_PARAM_NUMBER}_0_72"
    ).replace("-", "")


@pytest.mark.asyncio
async def test_equipment_parameter_number_name(hass, manager: Manager, caplog):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)
    assert c.name == f"{system.name}_par_{parameter.name}".replace(" ", "_")


@pytest.mark.asyncio
async def test_equipment_parameter_number_unit_of_measure(
    hass, manager: Manager, caplog
):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)
    assert c.unit_of_measurement == TEMP_FAHRENHEIT


@pytest.mark.asyncio
async def test_equipment_parameter_number_max_value(hass, manager: Manager, caplog):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)
    assert c.max_value == float(parameter.range_max)


@pytest.mark.asyncio
async def test_equipment_parameter_number_min_value(hass, manager: Manager, caplog):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)
    assert c.min_value == float(parameter.range_min)


@pytest.mark.asyncio
async def test_equipment_parameter_number_step(hass, manager: Manager, caplog):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)
    assert c.step == float(parameter.range_inc)


@pytest.mark.asyncio
async def test_equipment_parameter_number_value(hass, manager: Manager, caplog):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)
    assert c.value == parameter.value


@pytest.mark.asyncio
async def test_equipment_parameter_number_set_value(hass, manager: Manager, caplog):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)

    with patch.object(
        system, "set_equipment_parameter_value"
    ) as set_equipment_parameter_value:
        await c.async_set_native_value(60.0)
        assert set_equipment_parameter_value.call_count == 1
        set_equipment_parameter_value.await_args[0][0] == equipment.equipment_id
        set_equipment_parameter_value.await_args[0][1] == parameter.pid
        set_equipment_parameter_value.await_args[0][2] == "60.0"

    manager.parameter_safety_turn_on(system.sysId)
    with patch.object(
        system, "set_equipment_parameter_value"
    ) as set_equipment_parameter_value:
        ex: HomeAssistantError = None
        try:
            await c.async_set_native_value(60.0)
        except HomeAssistantError as e:
            ex = e
        assert ex != None
        assert set_equipment_parameter_value.call_count == 0
        s = str(ex)
        assert "Unable to set parameter" in s
        assert c._myname in s
        assert "safety switch is on" in s

    manager.parameter_safety_turn_off(system.sysId)
    with patch.object(
        system, "set_equipment_parameter_value"
    ) as set_equipment_parameter_value:
        await c.async_set_native_value(60.0)
        assert set_equipment_parameter_value.call_count == 1
        set_equipment_parameter_value.await_args[0][0] == equipment.equipment_id
        set_equipment_parameter_value.await_args[0][1] == parameter.pid
        set_equipment_parameter_value.await_args[0][2] == "60.0"

    with caplog.at_level(logging.ERROR):
        with patch.object(
            system, "set_equipment_parameter_value"
        ) as set_equipment_parameter_value:
            caplog.clear()
            set_equipment_parameter_value.side_effect = S30Exception(
                "This is the error", 100, 200
            )
            await c.async_set_native_value(101)
            assert len(caplog.records) == 1
            assert (
                "EquipmentParameterNumber::async_set_native_value" in caplog.messages[0]
            )
            assert "This is the error" in caplog.messages[0]
            assert "101" in caplog.messages[0]

    with caplog.at_level(logging.ERROR):
        with patch.object(
            system, "set_equipment_parameter_value"
        ) as set_equipment_parameter_value:
            caplog.clear()
            set_equipment_parameter_value.side_effect = Exception("This is the error")
            await c.async_set_native_value(1)
            assert len(caplog.records) == 1
            assert (
                "EquipmentParameterNumber::async_set_native_value unexpected exception - please raise an issue"
                in caplog.messages[0]
            )


@pytest.mark.asyncio
async def test_equipment_parameter_number_device_info(hass, manager: Manager, caplog):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    await manager.create_devices()
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)
    identifiers = c.device_info["identifiers"]
    for x in identifiers:
        assert x[0] == LENNOX_DOMAIN
        assert x[1] == manager.system_equip_device_map[system.sysId][0].unique_name


@pytest.mark.asyncio
async def test_equipment_parameter_number_subscription(hass, manager: Manager, caplog):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)
    await c.async_added_to_hass()

    with patch.object(c, "schedule_update_ha_state") as update_callback:
        system.executeOnUpdateCallbacksEqParameters("0_72")
        assert update_callback.call_count == 1
        assert c.available == True

    with patch.object(c, "schedule_update_ha_state") as update_callback:
        manager.updateState(DS_RETRY_WAIT)
        assert update_callback.call_count == 1
        assert c.available == False

    with patch.object(c, "schedule_update_ha_state") as update_callback:
        manager.updateState(DS_CONNECTED)
        assert update_callback.call_count == 1
        assert c.available == True
        system.attr_updater({"status": "online"}, "status", "cloud_status")
        system.executeOnUpdateCallbacks()
        assert update_callback.call_count == 2
        assert c.available == True
        system.attr_updater({"status": "offline"}, "status", "cloud_status")
        system.executeOnUpdateCallbacks()
        assert update_callback.call_count == 3
        assert c.available == False


def test_equipment_parameter_number_entity_category(hass, manager: Manager, caplog):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)
    assert c.entity_category == "config"


def test_equipment_parameter_number_mode(hass, manager: Manager, caplog):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)
    assert c.mode == "box"


def test_equipment_parameter_select_extra_attributes(hass, manager: Manager, caplog):
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[72]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)
    conftest_parameter_extra_attributes(c.extra_state_attributes, equipment, parameter)


@pytest.mark.asyncio
async def test_equipment_parameter_number_set_zonetest_parameter(
    hass, manager_system_04_furn_ac_zoning: Manager, caplog
):
    manager = manager_system_04_furn_ac_zoning
    system: lennox_system = manager._api._systemList[0]
    equipment = system.equipment[0]
    parameter = equipment.parameters[256]
    c = EquipmentParameterNumber(hass, manager, system, equipment, parameter)

    with patch.object(
        system, "set_zone_test_parameter_value"
    ) as set_zone_test_parameter_value:
        await c.async_set_zonetest_parameter(60.0, True)
        assert set_zone_test_parameter_value.call_count == 1
        set_zone_test_parameter_value.await_args[0][0] == parameter.pid
        set_zone_test_parameter_value.await_args[0][1] == "60.0"
        set_zone_test_parameter_value.await_args[0][2] == True

    with patch.object(
        system, "set_zone_test_parameter_value"
    ) as set_zone_test_parameter_value:
        await c.async_set_zonetest_parameter(70.0, False)
        assert set_zone_test_parameter_value.call_count == 1
        set_zone_test_parameter_value.await_args[0][0] == parameter.pid
        set_zone_test_parameter_value.await_args[0][1] == "70.0"
        set_zone_test_parameter_value.await_args[0][2] == False

    with caplog.at_level(logging.ERROR):
        with patch.object(
            system, "set_zone_test_parameter_value"
        ) as set_zone_test_parameter_value:
            caplog.clear()
            set_zone_test_parameter_value.side_effect = S30Exception(
                "This is the error", 100, 200
            )
            await c.async_set_zonetest_parameter(70.0, False)
            assert len(caplog.records) == 1
            assert (
                "EquipmentParameterNumber::async_set_zonetest_parameter"
                in caplog.messages[0]
            )
            assert "This is the error" in caplog.messages[0]
            assert "70.0" in caplog.messages[0]

    with caplog.at_level(logging.ERROR):
        with patch.object(
            system, "set_zone_test_parameter_value"
        ) as set_zone_test_parameter_value:
            caplog.clear()
            set_zone_test_parameter_value.side_effect = Exception("This is the error")
            await c.async_set_zonetest_parameter(70.0, False)
            assert len(caplog.records) == 1
            assert (
                "EquipmentParameterNumber::async_set_zonetest_parameter unexpected exception - please raise an issue"
                in caplog.messages[0]
            )