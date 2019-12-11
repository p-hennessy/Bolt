# Configuration

The global configuration file is \(by default\) at `/etc/bolt/config.yml`

It uses the [YAML](https://yaml.org/) markup language.

<table>
  <thead>
    <tr>
      <th style="text-align:left">Key</th>
      <th style="text-align:left">Type</th>
      <th style="text-align:left">Default</th>
      <th style="text-align:left">Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align:left">api_key</td>
      <td style="text-align:left"><code>str</code>
      </td>
      <td style="text-align:left">-</td>
      <td style="text-align:left"><b>Required</b>. API Token used to connect to Discord</td>
    </tr>
    <tr>
      <td style="text-align:left">name</td>
      <td style="text-align:left"><code>str</code>
      </td>
      <td style="text-align:left"><code>Bolt</code>
      </td>
      <td style="text-align:left">Some plugins may set the bot&apos;s name to this or refer to the bot with
        this</td>
    </tr>
    <tr>
      <td style="text-align:left">trigger</td>
      <td style="text-align:left"><code>str</code>
      </td>
      <td style="text-align:left"><code>.</code>
      </td>
      <td style="text-align:left">Trigger is used as the default prefix for invoking commands</td>
    </tr>
    <tr>
      <td style="text-align:left">log_level</td>
      <td style="text-align:left"><code>str</code>
      </td>
      <td style="text-align:left"><code>INFO</code>
      </td>
      <td style="text-align:left">
        <p>Must be one of:
          <br /><code>DEBUG</code>
        </p>
        <p><code>INFO</code>
        </p>
        <p><code>WARNING</code>
        </p>
        <p><code>ERROR</code>
        </p>
        <p><code>CRITICAL</code>
        </p>
      </td>
    </tr>
    <tr>
      <td style="text-align:left">log_dir</td>
      <td style="text-align:left"><code>str</code>
      </td>
      <td style="text-align:left"><code>/var/log/bolt</code>
      </td>
      <td style="text-align:left">Directory to put the Bot logs. Will appear in JSON format</td>
    </tr>
    <tr>
      <td style="text-align:left">worker_threads</td>
      <td style="text-align:left"><code>int</code>
      </td>
      <td style="text-align:left"><code>1</code>
      </td>
      <td style="text-align:left">Amount of <a href="https://en.wikipedia.org/wiki/Green_threads">green threads</a> for
        the bot to spin up. These are light threads, so numbers in the hundreds
        is okay</td>
    </tr>
    <tr>
      <td style="text-align:left">shard_total</td>
      <td style="text-align:left"><code>int</code>
      </td>
      <td style="text-align:left"><code>1</code>
      </td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">shard_id</td>
      <td style="text-align:left"><code>int</code>
      </td>
      <td style="text-align:left"><code>0</code>
      </td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">mongo_database_uri</td>
      <td style="text-align:left"><code>uri</code>
      </td>
      <td style="text-align:left"><code>mongodb://localhost:27017</code>
      </td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">mongo_database_username</td>
      <td style="text-align:left"><code>str</code>
      </td>
      <td style="text-align:left">-</td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">mongo_database_password</td>
      <td style="text-align:left"><code>str</code>
      </td>
      <td style="text-align:left">-</td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">mongo_database_use_tls</td>
      <td style="text-align:left"><code>boolean</code>
      </td>
      <td style="text-align:left">-</td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">webhook_enable</td>
      <td style="text-align:left"><code>boolean</code>
      </td>
      <td style="text-align:left"><code>false</code>
      </td>
      <td style="text-align:left">Turn on or off the Webhook feature. Some users may not want to use this
        disabling it prevents</td>
    </tr>
    <tr>
      <td style="text-align:left">webhook_port</td>
      <td style="text-align:left"><code>int</code>
      </td>
      <td style="text-align:left"><code>8080</code>
      </td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">backdoor_enable</td>
      <td style="text-align:left"><code>boolean</code>
      </td>
      <td style="text-align:left"><code>false</code>
      </td>
      <td style="text-align:left">Turn on or off the Backdoor server. Allows user to inspect internal state
        of the bot for debugging</td>
    </tr>
    <tr>
      <td style="text-align:left">backdoor_host</td>
      <td style="text-align:left"><code>ip_address</code>
      </td>
      <td style="text-align:left"><code>127.0.0.1</code>
      </td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">backdoor_port</td>
      <td style="text-align:left"><code>int</code>
      </td>
      <td style="text-align:left"><code>5000</code>
      </td>
      <td style="text-align:left"></td>
    </tr>
  </tbody>
</table>

