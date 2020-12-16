function [p_theta, p_salpha, p_alpha, p_beta, p_gamma, p_total] = calcularPotencias(n_electrodos, n_trials, pares, s_eeg_theta, s_eeg_salpha, s_eeg_alpha, s_eeg_beta, s_eeg_gamma)
 
    n_pares  = size(pares, 2);
    if n_pares
        right_h = zeros(1, n_trials*n_pares);
        left_h  = zeros(1, n_trials*n_pares);
        % Matrices con los índices (columnas) de los electrodos que forman los pares simétricos en
        % las matrices de los EEG (n_electrodos*n_trials columnas)
        for t = 1:n_trials
            right_h(1,1+(t-1)*n_pares:t*n_pares) = pares(1,:)+n_electrodos*(t-1);
            left_h(1,1+(t-1)*n_pares:t*n_pares)  = pares(2,:)+n_electrodos*(t-1);
        end
    end

    % Inicializamos las matrices donde se van a guardar las potencias
    p_theta   = zeros(1, n_trials*(n_electrodos+n_pares));
    p_salpha  = zeros(1, n_trials*(n_electrodos+n_pares));
    p_alpha   = zeros(1, n_trials*(n_electrodos+n_pares));
    p_beta    = zeros(1, n_trials*(n_electrodos+n_pares));
    p_gamma   = zeros(1, n_trials*(n_electrodos+n_pares));
    p_total   = zeros(1, n_trials*(n_electrodos+n_pares));
    
	% Densidades de potencia
    pd_theta   = s_eeg_theta.^2;
    pd_salpha  = s_eeg_salpha.^2;
    pd_alpha   = s_eeg_alpha.^2;
    pd_beta    = s_eeg_beta.^2;
    pd_gamma   = s_eeg_gamma.^2;
    
    % 1) Potencias absolutas en las diferentes bandas
    p_theta(1:n_electrodos*n_trials)   = mean(pd_theta);
    p_salpha(1:n_electrodos*n_trials)  = mean(pd_salpha);
    p_alpha(1:n_electrodos*n_trials)   = mean(pd_alpha);
    p_beta(1:n_electrodos*n_trials)    = mean(pd_beta);
    p_gamma(1:n_electrodos*n_trials)   = mean(pd_gamma);

    % 2) Potencia total
    p_total = p_theta + p_alpha + p_beta + p_gamma;

    if n_pares
        % 3) Asímetría potencias en cada banda entre pares de electrodos: [(R-L)/(R+L)]
        p_theta(n_trials*n_electrodos+1:end)   = (p_theta(:,right_h)   - p_theta(:,left_h))  ./ (p_theta(:,right_h)  + p_theta(:,left_h));
        p_salpha(n_trials*n_electrodos+1:end)  = (p_salpha(:,right_h)  - p_salpha(:,left_h)) ./ (p_salpha(:,right_h) + p_salpha(:,left_h));
        p_alpha(n_trials*n_electrodos+1:end)   = (p_alpha(:,right_h)   - p_alpha(:,left_h))  ./ (p_alpha(:,right_h)  + p_alpha(:,left_h));
        p_beta(n_trials*n_electrodos+1:end)    = (p_beta(:,right_h)    - p_beta(:,left_h))   ./ (p_beta(:,right_h)   + p_beta(:,left_h));
        p_gamma(n_trials*n_electrodos+1:end)   = (p_gamma(:,right_h)   - p_gamma(:,left_h))  ./ (p_gamma(:,right_h)  + p_gamma(:,left_h));

        % 4) Asímetría potencia total entre pares de electrodos : [(R-L)/(R+L)]
        p_total(n_trials*n_electrodos+1:end)   = (p_total(:,right_h)   - p_total(:,left_h))  ./ (p_total(:,right_h)  + p_total(:,left_h));
    end

    % Aplicar logaritmos a (1) y (2)
	% p_theta(1:n_electrodos*n_trials)   =	10*log10(p_theta(1:n_electrodos*n_trials)); 
	% p_salpha(1:n_electrodos*n_trials)  =	10*log10(p_salpha(1:n_electrodos*n_trials));
	% p_alpha(1:n_electrodos*n_trials)   =	10*log10(p_alpha(1:n_electrodos*n_trials)); 
	% p_beta(1:n_electrodos*n_trials)    =	10*log10(p_beta(1:n_electrodos*n_trials)); 
    % p_gamma(1:n_electrodos*n_trials)   =	10*log10(p_gamma(1:n_electrodos*n_trials));
    % p_total(1:n_electrodos*n_trials)   =    10*log10(p_total(1:n_electrodos*n_trials));
end