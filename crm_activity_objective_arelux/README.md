Implementa el addon crm_activity_objective con peculiaridades de Arelux

Los crones previamente existentes:
- Odoo Crm Lead Change Empty next_activity_objective_id
- Odoo Crm Lead Change Seguimiento
- Odoo Crm Lead Change Dormidos
- Odoo Crm Lead Change Inactivos

se optimizan de la siguiente forma:


## Crones
### Odoo Crm Lead Change Empty next_activity_objective_id
Modifica los flujos de ventas que corresponde para quitar el objetivo de siguiente actividad según diferentes criterios.

### Odoo Crm Lead Change Seguimiento
Modifica los flujos de ventas que corresponde para asignarles el objetivo de siguiente actividad a ‘Seguimiento’ según diferentes criterios.

### Odoo Crm Lead Change Dormidos
Modifica los flujos de ventas que corresponde para asignarles el objetivo de siguiente actividad a ‘Despertar’ según diferentes criterios.

Vinculado con el addon: crm_arelux 

Tienen los siguientes criterios:

#### Todocesped:

Marzo a Agosto (incluidos)
  - Tipo: Opotunidad
  - Activo: Si
  - Probabilidad: >0 y <100
  - Tipo de actividad (del cliente): Todocesped o Ambos
  - Tipo de cliente (del cliente): Profesional
  - Nº total pedidos (del cliente): >0
  - Nº total pedidos últimos 30 días (del cliente): =0
  - Objetivo de la siguiente actividad: NO sean “Excepción”, “Repaso”, “Cierre” y “Despertar”

Resto de meses (Septiembre a Febrero incluidos):
  - Tipo: Opotunidad
  - Activo: Si
  - Probabilidad: >0 y <100
  - Tipo de actividad (del cliente): Todocesped o Ambos
  - Tipo de cliente (del cliente): Profesional
  - Nº total pedidos (del cliente): >0
  - Nº total pedidos últimos 90 días (del cliente): =0
  - Objetivo de la siguiente actividad: NO sean “Excepción”, “Repaso”, “Cierre” y “Despertar”

#### Arelux

  - Tipo: Opotunidad
  - Activo: Si
  - Probabilidad: >0 y <100
  - Tipo de actividad (del cliente): Arelux
  - Tipo de cliente (del cliente): Profesional
  - Nº total pedidos (del cliente): >0
  - Nº total pedidos últimos 90 días (del cliente): =0
  - Objetivo de la siguiente actividad: NO sean “Excepción”, “Repaso”, “Cierre” y “Despertar”

Nota: Cuando se indica (del cliente) quiere decir que esa información también existe y se calcula en el lead pudiendo ser distinta en el lead de en el cliente.
Nota2: Este funcionamiento SOLO se aplica cuando hay definido un objetivo de siguiente actividad puesto que SIEMPRE debe estar uno definido (salvo que esté ganado o perdido el flujo).

*Nº total pedidos: Nº pedidos >300€ en BI
*Nº total pedidos últimos 30 días: Nº pedidos confirmados en los últimos 30 días >300€ en BI
*Nº total pedidos últimos 90 días: Nº pedidos confirmados en los últimos 90 días >300€ en BI


### Odoo Crm Lead Change Inactivos
Modifica los flujos de ventas que corresponde para asignarles el objetivo de siguiente actividad a ‘Activar’ según diferentes criterios.


Adicionalmente se definen estos otros crones:

### Odoo Res Partner Fields Generate
Frecuencia: 1 vez al día

Descripción:

Define los campos: total_sale_order, account_invoice_amount_untaxed_total, days_from_last_sale_order, days_from_last_message del modelo res.partner según lo definido en las vistas.

### Odoo Res Partner Fields Generate Days
Frecuencia: 1 vez al día

Descripción:

Re-define los campos: days_from_last_sale_order y days_from_last_message del modelo res.partner

### Odoo Crm Lead Fields Generate
Frecuencia: 1 vez al día

Descripción:

Define los campos: total_sale_order, total_sale_order_last_30_days, total_sale_order_last_90_days, account_invoice_amount_untaxed_total, days_from_last_sale_order, days_from_last_message del modelo crm.lead según lo definido en las vistas.

### Odoo Crm Lead Fields Generate Days
Frecuencia: 1 vez al día

Descripción:

Re-define los campos: days_from_last_sale_order y days_from_last_message del modelo crm.lead
