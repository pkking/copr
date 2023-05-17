srpm:                                                                                                                                                                                                                                       
	dnf -y install tito                                                                                                                                                                                                                 
	tito build --tgz --offline --output=$(dir $(spec))
	rpmbuild -bs -D '_sourcedir $(dir $(spec))' -D '_srcrpmdir $(outdir)' '$(spec)'
