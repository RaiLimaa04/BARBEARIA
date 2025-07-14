# 📊 Geração de Dados de Teste - Sistema Barbearia

Este documento explica como usar os scripts de geração de dados fictícios para testar o sistema da barbearia.

## 🚀 Comandos Disponíveis

### 1. Geração Completa de Dados
```bash
python manage.py generate_all_test_data
```
**O que faz:**
- Cria serviços, clientes e horários de funcionamento
- Gera agendamentos passados (histórico de 90 dias)
- Gera agendamentos futuros (próximos 30 dias)
- Mostra estatísticas completas

### 2. Apenas Configuração Inicial
```bash
python manage.py generate_all_test_data --setup-only
```
**O que faz:**
- Cria apenas serviços, clientes e horários de funcionamento
- Não gera agendamentos

### 3. Apenas Agendamentos
```bash
python manage.py generate_all_test_data --appointments-only
```
**O que faz:**
- Gera apenas agendamentos (passados e futuros)
- Requer que serviços, clientes e horários já existam

## ⚙️ Opções Personalizáveis

### Geração Completa com Parâmetros
```bash
python manage.py generate_all_test_data --days 60 --days-back 120 --appointments-per-day 8
```

**Parâmetros:**
- `--days`: Número de dias para agendamentos futuros (padrão: 30)
- `--days-back`: Número de dias para trás para histórico (padrão: 90)
- `--appointments-per-day`: Agendamentos por dia (padrão: 5)

### Comandos Individuais

#### Configurar Dados Básicos
```bash
python manage.py setup_test_data
```

#### Gerar Agendamentos Futuros
```bash
python manage.py generate_test_appointments --days 30 --appointments-per-day 5
```

#### Gerar Agendamentos Passados (Histórico)
```bash
python manage.py generate_past_appointments --days-back 90 --appointments-per-day 3
```

## 📋 Dados Gerados

### Serviços Criados
- Corte Masculino (R$ 35,00 - 30 min)
- Barba (R$ 25,00 - 20 min)
- Corte + Barba (R$ 50,00 - 45 min)
- Corte Infantil (R$ 25,00 - 25 min)
- Hidratação (R$ 40,00 - 30 min)
- Pigmentação (R$ 60,00 - 60 min)
- Sobrancelha (R$ 15,00 - 15 min)
- Pacote Completo (R$ 90,00 - 90 min)

### Clientes Criados
- 10 clientes fictícios com dados completos
- Usuários: joao.silva, pedro.santos, carlos.oliveira, etc.
- Senha padrão: `123456`
- Telefones no formato (11) 99999-XXXX

### Horários de Funcionamento
- **Segunda a Sexta:** 09:00 - 18:00
- **Sábado:** 08:00 - 17:00
- **Domingo:** Fechado

## 📊 Características dos Agendamentos

### Agendamentos Futuros
- 75% confirmados
- 20% cancelados
- 5% pendentes
- Horários distribuídos ao longo do dia
- Observações variadas

### Agendamentos Passados (Histórico)
- 80% confirmados
- 16% cancelados
- 4% pendentes
- Observações mais realistas para histórico

## 🔍 Como Verificar os Dados

### 1. Admin do Django
```bash
python manage.py runserver
```
Acesse: http://localhost:8000/admin

### 2. Verificar via Shell
```bash
python manage.py shell
```

```python
from core.models import Service, Cliente
from scheduling.models import Appointment

# Contar registros
print(f"Serviços: {Service.objects.count()}")
print(f"Clientes: {Cliente.objects.count()}")
print(f"Agendamentos: {Appointment.objects.count()}")

# Ver próximos agendamentos
from django.utils import timezone
upcoming = Appointment.objects.filter(
    date__gte=timezone.now().date(),
    is_cancelled=False
).order_by('date', 'time')[:10]

for apt in upcoming:
    print(f"{apt.date} {apt.time} - {apt.client_name}")
```

### 3. Estatísticas Detalhadas
```bash
python manage.py generate_all_test_data --setup-only
```

## 🧹 Limpar Dados de Teste

Para limpar todos os dados de teste:

```python
# No shell do Django
from core.models import Service, Cliente, BusinessHour
from scheduling.models import Appointment

# Limpar agendamentos
Appointment.objects.all().delete()

# Limpar clientes (opcional)
Cliente.objects.all().delete()

# Limpar serviços (opcional)
Service.objects.all().delete()

# Limpar horários (opcional)
BusinessHour.objects.all().delete()
```

## ⚠️ Observações Importantes

1. **Backup:** Sempre faça backup antes de executar os scripts
2. **Ambiente:** Execute apenas em ambiente de desenvolvimento/teste
3. **Dados Reais:** Os scripts não afetam dados de produção existentes
4. **Performance:** Para grandes volumes, execute em lotes menores

## 🎯 Exemplos de Uso

### Cenário 1: Teste Básico
```bash
python manage.py generate_all_test_data
```

### Cenário 2: Teste com Muitos Dados
```bash
python manage.py generate_all_test_data --days 60 --appointments-per-day 10
```

### Cenário 3: Apenas Histórico
```bash
python manage.py generate_past_appointments --days-back 180 --appointments-per-day 5
```

### Cenário 4: Dados Básicos + Poucos Agendamentos
```bash
python manage.py generate_all_test_data --setup-only
python manage.py generate_test_appointments --days 7 --appointments-per-day 3
```

## 📈 Estatísticas Esperadas

Com configuração padrão, você terá aproximadamente:
- 8 serviços
- 10 clientes
- 6 horários de funcionamento
- 270 agendamentos passados (90 dias × 3/dia)
- 150 agendamentos futuros (30 dias × 5/dia)
- **Total:** ~420 agendamentos

## 🆘 Solução de Problemas

### Erro: "Nenhum serviço encontrado"
```bash
python manage.py setup_test_data
```

### Erro: "Nenhum cliente encontrado"
```bash
python manage.py setup_test_data
```

### Erro: "Nenhum horário de funcionamento encontrado"
```bash
python manage.py setup_test_data
```

### Dados duplicados
Os scripts usam `get_or_create()`, então são seguros para execução múltipla. 