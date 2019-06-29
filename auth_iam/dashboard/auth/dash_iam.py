from dash import Dash
from flask import jsonify, make_response, redirect, request
from werkzeug.exceptions import BadRequest


class DashIam(Dash):

    def __init__(self, authorizer, *args, **kwargs):
        """Dash wrapper that validates resource access before replying.

        In order to see how the data is splitted and the objects processed, the
        internal Dash api for getting the layout, components and updating
        components has to be seen.

        Parameters
        ----------
        authorizer: dashboard.auth.auth.Authorizer
            An authorizer instance to validate allowed resources.
        """
        super().__init__(*args, **kwargs)
        self.authorizer = authorizer

    def dependencies(self):
        """Before returning dependencies, ensure that resources not allowed are
        filtered out."""
        dependencies = [{
                'output': k,
                'inputs': v['inputs'],
                'state': v['state'],
                'clientside_function': v.get('clientside_function', None)
            } for k, v in self.callback_map.items()
        ]
        allowed_resources = self._allowed_resources()
        if allowed_resources is not True:
            dependencies = self._filter_dependencies(
                dependencies, allowed_resources)
        return jsonify(dependencies)

    def dispatch(self):
        """Before dispatching, check if anything of the components touched,
        inputs or outputs belong to forbidden resources."""
        allowed_resources = self._allowed_resources()
        if allowed_resources is True:
            return super().dispatch()
        try:
            body = request.get_json()
            if self._not_allowed(
                    body.get('changedPropIds', []), allowed_resources):
                return self._redirect_response()
            if self._not_allowed(
                    (input_item.get('id', '') for input_item in
                     body.get('inputs', [])), allowed_resources):
                return self._redirect_response()
            if self._not_allowed(
                   body.get('output', '').strip('..').split('...'),
                   allowed_resources):
                return self._redirect_response()
            return super().dispatch()
        except (BadRequest, KeyError):
            pass
        return self._redirect_response()

    def _allowed_resources(self):
        """Returns the allowed resources the user can access.
        True if the user can access everything.
        Otherwise returns a list of component ids."""
        if not request:
            return True
        payload = self.authorizer.read_cookie(request)
        if isinstance(payload, dict):
            allowed_resources = payload.get('allowed_resources', [])
            if '_all_' in allowed_resources:
                return True
            return allowed_resources
        return []

    def _filter_dependencies(self, dependencies, allowed_resources):
        """Filters elements from the dependencies whose ids up to the first -
        are not in allowed_sections. If allowed_sections is _all_, the whole
        dependencies will be returned.

        Parameters
        ----------
        dependencies: [dict]
            The dash dependencies list.
        allowed_sections: [str]
            List of string of allowed prefixes. E.g.: overview.
            If the special _all_ prefix is contained, the whole layout will be
            returned.
        """
        return [
            dependency for dependency in dependencies
            if not (
               self._not_allowed(
                   (input_component.get('id', '')
                    for input_component in dependency.get('inputs', [])),
                   allowed_resources) or
               self._not_allowed(
                   (output_component for output_component in
                    dependency.get('output', '').strip('..').split('...')),
                   allowed_resources)
            )]

    @staticmethod
    def _not_allowed(ids, allowed_resources):
        """Checks if all the ids are allowed to be accessed.
        Ids that start with an underscore are ignored.

        Parameters
        ----------
        ids: [str]
        allowed_resources: [str]
        """
        return any(DashIam._id_prefix(id_) not in allowed_resources
                   for id_ in ids if not id_.startswith('_'))

    @staticmethod
    def _id_prefix(id_):
        """Returns the prefix of the id."""
        return id_.split('-', 1)[0]

    @staticmethod
    def _redirect_response():
        return make_response(redirect('/login'), 302)
