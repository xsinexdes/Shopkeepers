package com.nisovin.shopkeepers.medieval;

import org.bukkit.Location;
import org.bukkit.entity.Player;
import org.bukkit.util.RayTraceResult;

import com.nisovin.shopkeepers.SKShopkeepersPlugin;
import com.nisovin.shopkeepers.api.shopkeeper.Shopkeeper;

public final class Targeting {

	/** Devuelve el shopkeeper (mob) al que mira el jugador, o null. */
	public static Shopkeeper lookingAt(Player player, double range) {
		Location eye = player.getEyeLocation();
		RayTraceResult result = player.getWorld().rayTraceEntities(eye, eye.getDirection(), range,
				0.35D, entity -> SKShopkeepersPlugin.getInstance().getShopkeeperRegistry()
						.getShopkeeperByEntity(entity) != null);
		if (result == null || result.getHitEntity() == null) return null;
		return SKShopkeepersPlugin.getInstance().getShopkeeperRegistry()
				.getShopkeeperByEntity(result.getHitEntity());
	}

	private Targeting() {
	}
}
