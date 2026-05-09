package com.oran.chatgeologger;

import io.papermc.paper.event.player.AsyncChatEvent;
import net.kyori.adventure.text.Component;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Locale;

public final class ChatGeoLogger extends JavaPlugin implements Listener {

    private BufferedWriter writer;
    private String experimentId;

    @Override
    public void onEnable() {
        try {
            // Copies config.yml from JAR to plugins/ChatGeoLogger/config.yml (first run only)
            saveDefaultConfig();
            experimentId = getConfig().getString("experimentId", "exp_default");

            File logDir = new File(getDataFolder(), "logs");
            if (!logDir.exists()) logDir.mkdirs();

            File out = new File(logDir, "chat_geo.jsonl");
            writer = new BufferedWriter(
                    new OutputStreamWriter(new FileOutputStream(out, true), StandardCharsets.UTF_8)
            );

            Bukkit.getPluginManager().registerEvents(this, this);
            getLogger().info("ChatGeoLogger enabled (experimentId=" + experimentId + ")");
        } catch (Exception e) {
            getLogger().severe("Failed to start ChatGeoLogger: " + e.getMessage());
            Bukkit.getPluginManager().disablePlugin(this);
        }
    }

    @Override
    public void onDisable() {
        try {
            if (writer != null) writer.close();
        } catch (IOException ignored) {}
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onChat(AsyncChatEvent event) {
        String name = event.getPlayer().getName();
        boolean isAgent = name.startsWith("Agent_");

        Location loc = event.getPlayer().getLocation();
        String msg = toPlain(event.message());

        String json = "{"
                + "\"ts\":\"" + Instant.now() + "\","
                + "\"experimentId\":\"" + esc(experimentId) + "\","
                + "\"name\":\"" + esc(name) + "\","
                + "\"uuid\":\"" + event.getPlayer().getUniqueId() + "\","
                + "\"isAgent\":" + isAgent + ","
                + "\"msg\":\"" + esc(msg) + "\","
                + "\"world\":\"" + esc(loc.getWorld().getName()) + "\","
                + "\"x\":" + fmt(loc.getX()) + ","
                + "\"y\":" + fmt(loc.getY()) + ","
                + "\"z\":" + fmt(loc.getZ())
                + "}";

        write(json);
    }

    private synchronized void write(String line) {
        try {
            writer.write(line);
            writer.write("\n");
            writer.flush();
        } catch (IOException e) {
            getLogger().warning("Write failed: " + e.getMessage());
        }
    }

    private static String toPlain(Component c) {
        return net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer.plainText().serialize(c);
    }

    private static String esc(String s) {
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r");
    }

    private static String fmt(double d) {
        return String.format(Locale.US, "%.2f", d);
    }
}

