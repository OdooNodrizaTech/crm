El módulo contiene el desarrollo que permite implementar objetivos de actividad

## Crones

### Odoo Crm Lead Change Empty next_activity_objective_id
Frecuencia: 1 vez al día

Descripción:

Modifica los flujos de ventas que corresponde para quitar el objetivo de siguiente actividad según diferentes criterios.

### Odoo Crm Lead Change Seguimiento
Frecuencia: 1 vez al día

Descripción:

Modifica los flujos de ventas que corresponde para asignarles el objetivo de siguiente actividad a ‘Seguimiento’ según diferentes criterios.

### Odoo Crm Lead Change Dormidos
Frecuencia: 1 vez al día

Descripción:

Modifica los flujos de ventas que corresponde para asignarles el objetivo de siguiente actividad a ‘Despertar’ según diferentes criterios.

Vinculado con el addon: crm_arelux

Tienen los siguientes criterios:

Todocesped:
Marzo a Agosto (incluidos)

Tipo: Opotunidad
Activo: Si
Probabilidad: >0 y <100
Tipo de actividad (del cliente): Todocesped o Ambos
Tipo de cliente (del cliente): Profesional
Nº total pedidos (del cliente): >0
Nº total pedidos últimos 30 días (del cliente): =0
Objetivo de la siguiente actividad: NO sean “Excepción”, “Repaso”, “Cierre” y “Despertar”
Resto de meses (Septiembre a Febrero incluidos):

Tipo: Opotunidad
Activo: Si
Probabilidad: >0 y <100
Tipo de actividad (del cliente): Todocesped o Ambos
Tipo de cliente (del cliente): Profesional
Nº total pedidos (del cliente): >0
Nº total pedidos últimos 90 días (del cliente): =0
Objetivo de la siguiente actividad: NO sean “Excepción”, “Repaso”, “Cierre” y “Despertar”
Arelux
Tipo: Opotunidad
Activo: Si
Probabilidad: >0 y <100
Tipo de actividad (del cliente): Arelux
Tipo de cliente (del cliente): Profesional
Nº total pedidos (del cliente): >0
Nº total pedidos últimos 90 días (del cliente): =0
Objetivo de la siguiente actividad: NO sean “Excepción”, “Repaso”, “Cierre” y “Despertar”
Nota: Cuando se indica (del cliente) quiere decir que esa información también existe y se calcula en el lead pudiendo ser distinta en el lead de en el cliente. Nota2: Este funcionamiento SOLO se aplica cuando hay definido un objetivo de siguiente actividad puesto que SIEMPRE debe estar uno definido (salvo que esté ganado o perdido el flujo).

*Nº total pedidos: Nº pedidos >300€ en BI *Nº total pedidos últimos 30 días: Nº pedidos confirmados en los últimos 30 días >300€ en BI *Nº total pedidos últimos 90 días: Nº pedidos confirmados en los últimos 90 días >300€ en BI

### Odoo Crm Lead Change Inactivos
Frecuencia: 1 vez al día

Descripción:

Modifica los flujos de ventas que corresponde para asignarles el objetivo de siguiente actividad a ‘Activar’ según diferentes criterios.
