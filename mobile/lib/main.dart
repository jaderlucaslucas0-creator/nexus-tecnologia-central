import 'package:flutter/material.dart';

void main() {
  runApp(const NexusGestaoApp());
}

class NexusGestaoApp extends StatelessWidget {
  const NexusGestaoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Nexus Gestão',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1769E0)),
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF5F7FB),
      ),
      home: const LoginPage(),
    );
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  bool obscure = true;

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  void login() {
    if (emailController.text.trim().isEmpty ||
        passwordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Preencha e-mail e senha.')),
      );
      return;
    }

    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const DashboardPage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(28),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Icon(Icons.hub_rounded, size: 64, color: Color(0xFF1769E0)),
                      const SizedBox(height: 12),
                      Text('NEXUS GESTÃO', textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 6),
                      const Text('Gestão inteligente para sua clínica', textAlign: TextAlign.center),
                      const SizedBox(height: 28),
                      TextField(
                        controller: emailController,
                        keyboardType: TextInputType.emailAddress,
                        decoration: const InputDecoration(labelText: 'E-mail', prefixIcon: Icon(Icons.email_outlined), border: OutlineInputBorder()),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: passwordController,
                        obscureText: obscure,
                        decoration: InputDecoration(labelText: 'Senha', prefixIcon: const Icon(Icons.lock_outline), border: const OutlineInputBorder(), suffixIcon: IconButton(onPressed: () => setState(() => obscure = !obscure), icon: Icon(obscure ? Icons.visibility : Icons.visibility_off))),
                      ),
                      const SizedBox(height: 22),
                      FilledButton(onPressed: login, child: const Padding(padding: EdgeInsets.all(12), child: Text('Entrar'))),
                      TextButton(onPressed: () => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Recuperação será conectada à API.'))), child: const Text('Esqueci minha senha')),
                      OutlinedButton.icon(onPressed: () => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Login por WhatsApp será ativado nas configurações da API.'))), icon: const Icon(Icons.chat_outlined), label: const Text('Entrar com WhatsApp')),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  int index = 0;

  final pages = const [
    HomeTab(),
    PatientsTab(),
    ScheduleTab(),
    MoreTab(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nexus Gestão'), actions: [IconButton(onPressed: () {}, icon: const Icon(Icons.notifications_none))]),
      body: pages[index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (value) => setState(() => index = value),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard), label: 'Início'),
          NavigationDestination(icon: Icon(Icons.people_outline), selectedIcon: Icon(Icons.people), label: 'Pacientes'),
          NavigationDestination(icon: Icon(Icons.calendar_month_outlined), selectedIcon: Icon(Icons.calendar_month), label: 'Agenda'),
          NavigationDestination(icon: Icon(Icons.menu), label: 'Mais'),
        ],
      ),
    );
  }
}

class HomeTab extends StatelessWidget {
  const HomeTab({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(padding: const EdgeInsets.all(16), children: [
      Text('Olá, profissional', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
      const SizedBox(height: 4),
      const Text('Veja um resumo da sua gestão hoje.'),
      const SizedBox(height: 20),
      GridView.count(crossAxisCount: 2, shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), crossAxisSpacing: 12, mainAxisSpacing: 12, childAspectRatio: 1.35, children: const [
        SummaryCard(title: 'Pacientes', value: '0', icon: Icons.people, color: Colors.blue),
        SummaryCard(title: 'Sessões hoje', value: '0', icon: Icons.event_available, color: Colors.green),
        SummaryCard(title: 'Receitas', value: 'R$ 0,00', icon: Icons.attach_money, color: Colors.orange),
        SummaryCard(title: 'Pendências', value: '0', icon: Icons.pending_actions, color: Colors.red),
      ]),
      const SizedBox(height: 20),
      Card(child: ListTile(leading: const Icon(Icons.auto_awesome, color: Colors.blue), title: const Text('Assistente Nexus IA'), subtitle: const Text('Resumos e relatórios serão gerados com revisão humana.'), trailing: const Icon(Icons.chevron_right))),
    ]);
  }
}

class SummaryCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;
  const SummaryCard({super.key, required this.title, required this.value, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) => Card(child: Padding(padding: const EdgeInsets.all(14), child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Icon(icon, color: color), Text(title), Text(value, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold))])));
}

class PatientsTab extends StatelessWidget {
  const PatientsTab({super.key});
  @override
  Widget build(BuildContext context) => EmptyModule(icon: Icons.people_outline, title: 'Pacientes', description: 'Cadastre, pesquise e acompanhe os pacientes da clínica.', action: 'Cadastrar paciente');
}

class ScheduleTab extends StatelessWidget {
  const ScheduleTab({super.key});
  @override
  Widget build(BuildContext context) => EmptyModule(icon: Icons.calendar_month_outlined, title: 'Agenda', description: 'Organize consultas, sessões, horários e lembretes.', action: 'Nova sessão');
}

class MoreTab extends StatelessWidget {
  const MoreTab({super.key});
  @override
  Widget build(BuildContext context) => ListView(padding: const EdgeInsets.all(16), children: [
    const Text('Módulos', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
    const SizedBox(height: 12),
    ...[
      ['Prontuários', Icons.folder_shared_outlined], ['Sessões', Icons.psychology_outlined], ['Financeiro', Icons.account_balance_wallet_outlined], ['Relatórios', Icons.bar_chart_outlined], ['Profissionais', Icons.badge_outlined], ['Configurações', Icons.settings_outlined],
    ].map((item) => Card(child: ListTile(leading: Icon(item[1] as IconData, color: const Color(0xFF1769E0)), title: Text(item[0] as String), trailing: const Icon(Icons.chevron_right), onTap: () => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${item[0]} será conectado ao backend.')))))).toList(),
  ]);
}

class EmptyModule extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final String action;
  const EmptyModule({super.key, required this.icon, required this.title, required this.description, required this.action});
  @override
  Widget build(BuildContext context) => Center(child: Padding(padding: const EdgeInsets.all(28), child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(icon, size: 72, color: const Color(0xFF1769E0)), const SizedBox(height: 16), Text(title, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)), const SizedBox(height: 8), Text(description, textAlign: TextAlign.center), const SizedBox(height: 24), FilledButton.icon(onPressed: () => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$action será conectado ao banco de dados.'))), icon: const Icon(Icons.add), label: Text(action))])));
}
