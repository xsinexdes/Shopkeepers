# Shopkeepers Medieval (base Shopkeepers 2.24.0, solo Minecraft 1.21.1)

Este zip es el proyecto completo para compilar en GitHub. Solo incluye el modulo de 1.21.1
(`v1_21_R1`), asi que compila mas rapido y no depende de versiones nuevas.

## Como compilar en GitHub
1. Sube TODO el contenido de esta carpeta a tu repo (no la carpeta, su contenido).
2. Ve a *Actions* -> workflow **Build** (corre solo con cada push, o "Run workflow").
3. Descarga el artifact. El jar bueno es el que se llama `Shopkeepers-2.24.0...jar` (el grande,
   con todo adentro). Ignora los jar `shopkeepers-main` / `shopkeepers-api` sueltos.
4. Ponlo en `plugins/` de tu servidor Spigot/Paper 1.21.1 (Java 21).

## Archivos nuevos / modificados
- NUEVO `modules/main/src/main/java/com/nisovin/shopkeepers/medieval/**` (todo el codigo nuevo)
- NUEVO `modules/main/src/main/resources/medieval.yml` (configuracion de todo)
- MOD  `ui/trading/TradingView.java` (precio dinamico + registro de demanda)
- MOD  `SKShopkeepersPlugin.java` (arranca/apaga el modulo medieval)
- MOD  `plugin.yml` (comandos y permisos)
- MOD  `settings.gradle`, `modules/dist/build.gradle`, `scripts/installSpigotDependencies.sh`,
       `build.gradle`, `.github/workflows/build.yml` (solo 1.21.1, sin SonarCloud)
- NUEVO `resourcepack/` + `resourcepack_src/build_rp.py`

## Mercado (oferta y demanda estilo Albion)
- Cada compra en una tienda sube la demanda del objeto; cada venta de un jugador a una tienda
  de compra la baja. La demanda se recupera sola (vida media configurable).
- El precio de las **tiendas de admin** sigue el multiplicador (min x0.5, max x2.5 por defecto).
  Las tiendas de jugadores NO cambian: cada dueno pone su precio. Sus ventas si cuentan como demanda.
- Solo se ajustan tiendas que cobran/pagan en monedas (las de trueque no).
- `/mercado` menu con todos los objetos, tendencia y precio. Click en uno = **grafica**
  (9 columnas, 4 periodos, verde = barato, rojo = caro).
- `/mercado precio|grafica|eventos`
- Eventos: Feria, Escasez de hierro, Guerra, Gran cosecha, Hambruna, Fiebre del oro
  (editables en `medieval.yml`, tambien aleatorios cada hora con probabilidad configurable).
- Admin: `/mercadoadmin evento iniciar <plantilla> [min]`, `evento parar <id|todos>`,
  `evento listar|plantillas`, `evento crear <mult> <min> <ITEMS,coma|*> <nombre>`,
  `demanda <ITEM> <valor>`, `info <ITEM>`, `reiniciar [ITEM|todo]`, `recargar`, `guardar`.
- Un jugador que ya tiene el menu de comercio abierto ve los precios al abrirlo; para ver un
  cambio nuevo debe volver a abrir la tienda.

## Banco
- `/banco` abre el menu (depositar/retirar monedas base y altas). `/banco saldo|depositar|retirar|pagar`.
- Banquero NPC: mira a un mercader de admin (con al menos 1 trade) y usa `/bancoadmin npc`.
  Al hacerle click abre el banco.
- Admin: `/bancoadmin ver|dar|quitar|fijar <jugador> <monto>`, `top`, `npc`.
- Opcional en `medieval.yml`: limite de saldo, interes por hora, impuesto de transferencias.

## Rutas de mercaderes
- Mira al mercader, parate donde quieres que este y escribe `/ruta agregar 09:30`.
  Repite con otras horas/lugares. Hora = reloj de Minecraft (06:00 amanecer).
- A esa hora el mercader **camina** (buscador de caminos, esquiva paredes y desniveles de 1-3
  bloques) y se queda ahi. Siguen siendo invulnerables y sin IA como cualquier mercader.
- Si el chunk no esta cargado, el destino es muy lejano o no hay camino, aparece directo.
- `/ruta listar|quitar <n>|limpiar|ir <n>|estado|seleccionar`

## Resourcepack medieval (opcional)
1. Sube `resourcepack/ShopkeepersMedieval.zip` a un hosting con link directo.
2. En `medieval.yml`: `gui.usar-resourcepack: true`, y pon `gui.resourcepack.url`/`sha1`
   (o ponlo en server.properties). Hay que recargar: `/mercadoadmin recargar`.
3. Los botones usan PAPER + CustomModelData 1001-1013; los fondos usan una fuente (glifos
   E000-E002). Puedes cambiar las texturas editando los PNG o `resourcepack_src/build_rp.py`.
