# PIP Solar ESPHome External Component

PIP Solar ESPHome external component based on the existing pipsolar component.

## PV charging current over 50A

This version extends the supported maximum PV charging-current values to:

10A, 20A, 30A, 40A, 50A, 60A, 70A, 80A, 90A, 100A, 110A.

The PV charging current command uses the `MNCHGC0xxx` command format.

## ESPHome

```yaml
external_components:
  - source: github://Nguyenhoang823/pipsolar@main
    refresh: 5min

pipsolar:
  - uart_id: uart_bus
    id: effekta_ax
```

The component files are under `components/pipsolar/`.
