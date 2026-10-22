package com.nisovin.shopkeepers.medieval;

import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;

import com.nisovin.shopkeepers.api.events.ShopkeeperOpenUIEvent;
import com.nisovin.shopkeepers.api.ui.DefaultUITypes;
import com.nisovin.shopkeepers.medieval.gui.BankMenu;

final class EconomyListener implements Listener {

	private final MedievalEconomy economy;

	EconomyListener(MedievalEconomy economy) {
		this.economy = economy;
	}

	// Un mercader marcado como banquero abre el banco en vez del comercio.
	@EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
	void onOpenUI(ShopkeeperOpenUIEvent event) {
		if (!economy.config().getBoolean("banco.habilitado", true)) return;
		if (!DefaultUITypes.TRADING().equals(event.getUIType())) return;
		if (!economy.bank().isBanker(event.getShopkeeper().getUniqueId())) return;
		event.setCancelled(true);
		Player player = event.getPlayer();
		Bukkit.getScheduler().runTask(economy.getPlugin(), () -> {
			if (player.isOnline()) new BankMenu(economy, player).open();
		});
	}

	@EventHandler
	void onJoin(PlayerJoinEvent event) {
		if (!economy.config().getBoolean("gui.resourcepack.enviar-al-entrar", false)) return;
		String url = economy.config().getString("gui.resourcepack.url", "");
		if (url == null || url.isEmpty()) return;
		String sha1 = economy.config().getString("gui.resourcepack.sha1", "");
		Player player = event.getPlayer();
		Bukkit.getScheduler().runTaskLater(economy.getPlugin(), () -> {
			if (!player.isOnline()) return;
			if (sha1 != null && sha1.length() == 40) {
				player.setResourcePack(url, hex(sha1));
			} else {
				player.setResourcePack(url);
			}
		}, 40L);
	}

	private static byte[] hex(String s) {
		byte[] out = new byte[s.length() / 2];
		for (int i = 0; i < out.length; i++) {
			out[i] = (byte) Integer.parseInt(s.substring(i * 2, i * 2 + 2), 16);
		}
		return out;
	}
}
