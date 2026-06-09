# Guia Admin - Tipificaciones y Arbol de Gestion

## Objetivo

Permitir que Admin Empresa o SuperAdmin configure arboles de gestion sin tocar codigo.

## Componentes

- Arbol: define modulo, tenant, proyecto opcional y estado.
- Nodo: define nivel, padre, etiqueta, orden, color y efectos.
- Combinacion: define una ruta valida y sus campos obligatorios.

## Permisos

- `typifications.view`
- `typifications.manage`
- `typifications.trees.manage`
- `typifications.combinations.manage`

## Ejemplo

Contacto efectivo -> Promesa de pago exige valor, fecha y nota. El efecto cambia estado del cliente a Promesa y define siguiente accion.

## Reglas

No se permite operar arboles de otro tenant. El superadmin Icodeup puede ver y administrar globalmente.
