# Service Clean

App completo de busca e agendamento de profissionais de serviços
(diarista, eletricista, encanador etc.), com pagamento Pix e **split
automático de 10% de comissão para o app**, feito em Python com
`customtkinter` + `SQLite`.

## Como rodar

```bash
pip install customtkinter bcrypt requests
python main.py
```

**Login de teste:** `teste@gmail.com` / `Senha123!`

## Estrutura dos arquivos

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Ponto de entrada. Toda a interface e navegação entre telas (login, cadastro, catálogo, lista de profissionais, perfil, checkout, pós-checkout, meus agendamentos). |
| `database.py` | Camada única de acesso ao SQLite: usuários, profissionais, disponibilidade, agendamentos e pagamentos. |
| `dados_profissionais.py` | Dados de exemplo (seed) dos profissionais cadastrados, incluindo a chave Pix de cada um. |
| `pagamento.py` | Integração com o gateway de pagamento e a regra de **split automático** (90% profissional / 10% app). |
| `config.py` | Configurações centrais: cores da interface, percentual de comissão e credenciais do gateway (via variáveis de ambiente). |
| `seguranca.py` | Mascaramento de dados sensíveis (e-mail, chave Pix), validação de força de senha e sanitização de entradas. |
| `modulo_compartilhamento.py` | Gera texto e link de WhatsApp para o cliente indicar um profissional. |

> Os antigos arquivos `tela inicial` e `pagina de login` foram unificados
> na tela de login do `main.py` (eram a mesma tela duplicada). O mesmo
> vale para `tela principal(serviços)` e `fluxo de profissionais`, que
> viraram o catálogo + lista de profissionais.

## 💰 Como funciona a comissão de 10%

Toda vez que um pagamento é confirmado:

- **90%** do valor vai para a chave Pix do **profissional** (cadastrada em `dados_profissionais.py` / tabela `profissionais`)
- **10%** vai automaticamente para a sua chave Pix: **`elyoenaydb@gmail.com`** (banco Sicredi), configurada em `config.py`

Isso é feito através do recurso de **split de pagamento** do gateway —
ou seja, o dinheiro nunca "passa" pela sua conta pessoal ou pelo app
para depois ser repassado: o próprio gateway já entrega a parte certa
para cada chave no momento da confirmação do Pix. É o mesmo modelo usado
por apps como iFood, Uber e 99 para pagar seus prestadores.

### ⚠️ Isso ainda não move dinheiro de verdade — e é assim de propósito

Sem uma conta em um gateway de pagamento configurada, o app roda em
**modo simulado**: ele calcula os 90%/10% certinho e mostra tudo na
tela, mas nenhuma cobrança real é gerada. Isso é necessário porque:

1. Eu não tenho como criar uma conta de gateway de pagamento por você — isso exige seus próprios documentos (CPF/CNPJ) e passa por verificação de identidade (KYC), como qualquer conta bancária/PSP.
2. Cada gateway tem seu próprio formato de API para split (o código usa o Asaas como exemplo, mas o formato de "walletId" muda entre provedores).

### Para ativar pagamentos de verdade

1. Crie uma conta em um gateway brasileiro com **Pix + split via API**:
   - [Asaas](https://www.asaas.com/api) (mais simples para começar)
   - [Efí / Gerencianet](https://sejaefi.com.br)
   - [Mercado Pago](https://www.mercadopago.com.br/developers)
   - [PagBank](https://dev.pagbank.uol.com.br)
2. Cadastre sua conta pessoal (Sicredi, `elyoenaydb@gmail.com`) como a
   conta principal/recebedora da comissão.
3. Cadastre cada profissional como **subconta/recebedor** no gateway —
   você vai receber um ID (ex: `walletId` no Asaas) para cada um; troque
   esse ID no lugar da `pix_key` usada hoje como exemplo.
4. Configure as variáveis de ambiente antes de rodar o app:
   ```bash
   export SERVICE_CLEAN_GATEWAY_API_KEY="sua_chave_aqui"
   export SERVICE_CLEAN_GATEWAY_BASE_URL="https://api.asaas.com/v3"
   ```
5. Implemente a validação do **webhook** de confirmação de pagamento do
   gateway escolhido (essencial para não liberar o agendamento antes do
   Pix realmente cair — isso ainda não está incluso e exige o passo 4
   feito primeiro, já que depende do formato de cada provedor).

## Próximos passos sugeridos

- Tela de cadastro/edição de profissionais (hoje só existe o seed inicial)
- Recuperação de senha por e-mail
- Notificação ao profissional quando um agendamento é confirmado
- Avaliação do serviço após o atendimento (novos comentários)
- 
