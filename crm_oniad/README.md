El módulo contiene el desarrollo para añadir funcionalidades nuevas al apartado de CRM

id | name | position
--- | --- | ---
1 | Teléfono | 1
2 | Chat | 2
3 | Manual | 3
4 | Automatización | 4
 

Se ha limitado la opción al crear una actividad para que NO se pueda crear sin fecha.

Cuando se cambia el tipo de lead (de lead a opportunity) tiene los siguientes datos por defecto:

En el caso de ser lead:

commercial_activity_type = 'hunter'
lead_oniad_type = 'catchment'


En el caso de ser opportunity:
commercial_activity_type = 'account'
lead_oniad_type = 'other'


A la hora de crear un lead existen las siguientes restricciones siempre que el campo is_survey (account_oniad) está definido a False:

En el caso de ser lead:

- Si commercial_activity_type!=hunter nos muestra el aviso: Una iniciativa debe tener el tipo de actividad comercial 'Hunter'
- Si lead_oniad_type!=catchment nos muestra el aviso: Una iniciativa debe tener el tipo de lead a 'Captacion'

En el caso de ser opportunity:

- Si el commercial_activity_type!=account nos muestra el aviso: Un flujo de ventas debe tener el tipo de actividad comercial 'Account'
- Si el lead_oniad_type!=catchment nos muestra el aviso: Un flujo de ventas no debe tener el tipo de lead 'Captacion'
