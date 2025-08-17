RegistrationTool: add method `principal_id_or_login_name_exists`.
This is factored out from the `isMemberIdAllowed` method, which now calls this after checking the allowed member id pattern.
[maurits]