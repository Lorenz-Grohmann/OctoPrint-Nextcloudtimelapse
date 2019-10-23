# coding=utf-8
from __future__ import absolute_import
import octoprint.plugin
import octoprint.events
import owncloud
import os


class NextcloudtimelapsePlugin(octoprint.plugin.SettingsPlugin, octoprint.plugin.TemplatePlugin,
							   octoprint.plugin.EventHandlerPlugin, octoprint.plugin.RestartNeedingPlugin):

	def get_settings_defaults(self):
		return dict(
			server_address=None,
			username=None,
			password=None,
			dir_path=None,
			delete=False,
		)

	def get_settings_restricted_paths(self):
		return dict(
			admin=[["username"], ["password"], ["server_address"], ["dir_path"], ["delete"]]
		)

	def get_template_configs(self):
		return [
			dict(type='settings', custom_bindings=False, template='nextcloudTimelapse_settings.jinja2')
		]

	def get_update_information(self):
		return dict(
			nextcloudTimelapse=dict(
				displayName="Nextcloud Timelapse Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="Lorenz-Grohmann",
				repo="OctoPrint-NextcloudTimelapse",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/Lorenz-Grohmann/OctoPrint-Nextcloudtimelapse/archive/{target_version}.zip"
			)
		)

	def on_event(self, event, data):
		if event == octoprint.events.Events.MOVIE_DONE:
			self.upload_to_nextcloud(data)

	def upload_to_nextcloud(self, data):
		oc = owncloud.Client(self._settings.get(["server_address"]))
		try:
			oc.login(self._settings.get(["username"]), self._settings.get(["password"]))
			oc.put_file(self._settings.get(["dir_path"]) + data["movie_basename"], data["movie"])
			self._logger.info(
				"Uploaded timelapse: %s to %s" % (data["movie_basename"], self._settings.get(["server_address"])))
		except Exception as e:
			self._logger.error("Unable to upload timelaps: " + str(e))
			return
		if self._settings.get(["delete"]):
			os.remove(data["movie"])
			self._logger.info("Deleted local Timelapse: %s" % data["movie_basename"])


__plugin_name__ = "Nextcloud Timelapse"


def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = NextcloudtimelapsePlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
