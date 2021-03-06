import datetime
import os
import sys

from GAN.helpers.enums import Conf


def generate_name_prefix(config):
	suffix = ""
	if config[Conf.NAME_SUFFIX] is not None:
		suffix = "_%s" % config[Conf.NAME_SUFFIX]
	if config[Conf.LIMITED_DATASET] is not None:
		dataset_name = "_%s" % config[Conf.LIMITED_DATASET][:-4]
	else:
		dataset_name = config[Conf.DATASET_SIZE]
	return "%s_ImgCap%s_%s_Vocab%s_Seq%s_Batch%s_EmbSize%s_%s_Noise%s_PreInit%s_Dataset%s%s" % (
		config[Conf.DATE],
		config[Conf.IMAGE_CAPTION],
		config[Conf.WORD_EMBEDDING],
		config[Conf.VOCAB_SIZE],
		config[Conf.MAX_SEQ_LENGTH],
		config[Conf.BATCH_SIZE],
		config[Conf.EMBEDDING_SIZE],
		config[Conf.NOISE_MODE],
		config[Conf.NOISE_SIZE],
		# config[Conf.MAX_LOSS_DIFF],
		config[Conf.PREINIT],
		dataset_name,
		suffix
	)


class GANLogger:
	def __init__(self, config, inference):
		self.exists = False
		print "config[Conf.MODELNAME]: %s" % config[Conf.MODELNAME]
		if config[Conf.MODELNAME] is not None:
			self.name_prefix = config[Conf.MODELNAME]
		else:
			self.name_prefix = generate_name_prefix(config)

		print "Initialize logging..."
		if not inference:
			self.create_dirs("GAN/GAN_log")
			self.create_model_folders_and_files()
			self.create_model_files()

	@staticmethod
	def create_dirs(directory):
		if not os.path.exists(directory):
			os.makedirs(directory)

	def create_model_files(self):
		text_filenames = ["comments", "loss", "model_summary", "eval"]
		for filename in text_filenames:
			f = open("GAN/GAN_log/%s/%s.txt" % (self.name_prefix, filename), 'a+')
			if filename == "loss":
				f.write(str(datetime.datetime.now()) + "\n")
			f.close()

	def create_model_folders_and_files(self):
		model_filepath = "GAN/GAN_log/%s/model_files/stored_weights" % self.name_prefix
		self.exists = os.path.isdir(model_filepath)
		self.create_dirs(model_filepath)

	def save_model(self, model, name):
		self.save_model_summary(model, name)
		self.save_to_json(model, name)

	def save_to_json(self, model, name):
		model_json = model.to_json()
		with open("GAN/GAN_log/%s/model_files/%s.json" % (self.name_prefix, name), "w+") as json_file:
			json_file.write(model_json)

	def save_loss(self, g_loss, d_loss, epoch, batch):
		loss_file = open("GAN/GAN_log/%s/loss.txt" % self.name_prefix, "a")
		loss_file.write("%s,%s,%s,%s\n" % (epoch, batch, g_loss, d_loss))
		loss_file.close()

	def save_loss_acc(self, g_loss, g_acc, d_loss_gen, d_acc_gen, d_loss_train, d_acc_train, epoch, batch):
		loss_file = open("GAN/GAN_log/%s/loss.txt" % self.name_prefix, "a")
		loss_file.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (
			epoch, batch, g_loss, g_acc, d_loss_gen, d_acc_gen, d_loss_train, d_acc_train))
		loss_file.close()

	def save_loss_acc_fake(self, g_loss, g_acc, d_loss_gen, d_acc_gen, d_loss_train, d_acc_train, epoch, batch, d_loss_fake_img, d_acc_fake_img):
		loss_file = open("GAN/GAN_log/%s/loss.txt" % self.name_prefix, "a")
		loss_file.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
			epoch, batch, g_loss, g_acc, d_loss_gen, d_acc_gen, d_loss_train, d_acc_train, d_loss_fake_img, d_acc_fake_img))
		loss_file.close()

	def save_model_weights(self, model, epoch, name, suffix=""):
		path = "GAN/GAN_log/%s/model_files/stored_weights/" % self.name_prefix
		if suffix != "":
			suffix = "-" + suffix
		model.save_weights(path + "%s-%s%s" % (name, epoch, suffix), True)

	def print_start_message(self):
		print "\n"
		print "#" * 100
		print "Starting network %s" % self.name_prefix
		print "#" * 100

	def get_generator_weights(self):
		path = "GAN/GAN_log/%s/model_files/stored_weights/" % self.name_prefix
		weigthfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
		generator_weights = []
		for weightfile in weigthfiles:
			if "generator" in weightfile:
				generator_weights.append(weightfile)
		generator_weights.sort(key=lambda x: int(x.split("-")[-1]))
		return generator_weights

	def get_discriminator_weights(self):
		path = "GAN/GAN_log/%s/model_files/stored_weights/" % self.name_prefix
		weigthfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
		d_weights = []
		for weightfile in weigthfiles:
			if "discriminator" in weightfile:
				d_weights.append(weightfile)
		d_weights.sort(key=lambda x: int(x.split("-")[-1]))
		return d_weights

	def save_model_summary(self, model, name=str()):
		summary_file = open("GAN/GAN_log/%s/model_summary.txt" % self.name_prefix, "a")
		orig_stdout = sys.stdout
		sys.stdout = summary_file
		print "%s" % name.upper()
		model.summary()
		print "\n"
		sys.stdout = orig_stdout
		summary_file.close()

	def write_to_comments_file(self, text):
		summary_file = open("GAN/GAN_log/%s/comments.txt" % self.name_prefix, "a")
		summary_file.write("%s\n" % text)
		summary_file.close()

	def save_eval_data(self, epoch, distinct_sentences, sentence_count, avg_bleu_score, avg_bleu_cosine, avg_bleu_tfidf,
	                   avg_bleu_wmd):
		eval_file = open("GAN/GAN_log/%s/eval.txt" % self.name_prefix, "a+")
		eval_file.write("%s,%s,%s,%s,%s,%s,%s\n" % (
		epoch, distinct_sentences, sentence_count, avg_bleu_score, avg_bleu_cosine, avg_bleu_tfidf, avg_bleu_wmd))
		eval_file.close()

	def get_eval_lines(self):
		eval_file = open("GAN/GAN_log/%s/eval.txt" % self.name_prefix, "r")
		lines = eval_file.readlines()
		eval_file.close()
		return lines

	def get_eval_file_path(self):
		return "GAN/GAN_log/%s/eval.txt" % self.name_prefix
