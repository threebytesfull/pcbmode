import json
import pcbmode.utils.messages as msg

def dictFromJsonFile(filename, error=True):
    """
    Open a JSON file and return its content as a dict
    """

    def checking_for_unique_keys(pairs):
        """
        Check if there are duplicate keys defined; this is useful
        for any hand-edited file

        This SO answer was useful here:
          http://stackoverflow.com/questions/16172011/json-in-python-receive-check-duplicate-key-error
        """
        result = dict()
        for key,value in pairs:
            if key in result:
                msg.error("duplicate key ('%s') specified in %s" % (key, filename), KeyError)
            result[key] = value
        return result

    json_data = {}

    try:
        with open(filename, 'r') as f:
            json_data = json.load(f, object_pairs_hook=checking_for_unique_keys)
    except (IOError, OSError):
        if error == True:
            msg.error("Couldn't open JSON file: %s" % filename, IOError)
        else:
            msg.info("Couldn't open JSON file: %s" % filename, IOError)

    return json_data
