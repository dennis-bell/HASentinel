# HASentinel

## Introduction

HASentinel is a custom component for Home Assistant that monitors the availability of entities and alerts users based on different urgency levels. Stay informed about the health of your devices and entities without sifting through the noise of multiple notifications.

## Installation

To install HASentinel:

1. Clone or download this repository and copy the `hasentinel` folder from `custom_components` to your Home Assistant's `custom_components` directory.
2. Restart Home Assistant to pick up the new component.
3. Configure the component as described in the Configuration section.

## Configuration

Example configuration:
```yaml
hasentinel:
  entities:
    - entity_id: switch.printer3d_power
      urgency: high
    - entity_id: sensor.remote_grote_slaapkamer_battery
      urgency: medium
